from __future__ import annotations
import argparse, json, urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright

VIEWPORTS=[(320,760),(390,844),(768,1024),(1024,768),(1280,720),(1440,900),(1920,1080)]
ROOT=Path(__file__).resolve().parents[1]
SELECTED_PATHWAYS=json.loads((ROOT/'web/selected-pathways.json').read_text(encoding='utf-8'))['pathways']

def no_horizontal_overflow(page):
    overflow=page.evaluate("Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)-document.documentElement.clientWidth")
    assert overflow <= 2, overflow

def focus_is_visible(page):
    style=page.evaluate("""() => { const e=document.activeElement; if(!e) return null; const s=getComputedStyle(e); return {focusVisible:e.matches(':focus-visible'),tag:e.tagName,id:e.id,cls:e.className,outlineStyle:s.outlineStyle,outlineWidth:s.outlineWidth,boxShadow:s.boxShadow}; }""")
    assert style and style['focusVisible'], style
    assert ((style['outlineStyle']!='none' and style['outlineWidth']!='0px') or style['boxShadow']!='none'), style

def tab_to_id(page,target_id,steps=40):
    for _ in range(steps):
        page.keyboard.press('Tab')
        if page.evaluate("document.activeElement && document.activeElement.id")==target_id: return
    raise AssertionError(f'could not tab to #{target_id}')

def tab_to_selector(page,selector,steps=160):
    for _ in range(steps):
        page.keyboard.press('Tab')
        if page.evaluate("(selector) => document.activeElement?.matches(selector) === true", selector):
            return
    active=page.evaluate("() => ({tag:document.activeElement?.tagName,id:document.activeElement?.id,cls:document.activeElement?.className})")
    raise AssertionError(f'could not keyboard-tab to {selector}; active={active}')

def record(checks,name,ok=True):
    assert ok, name
    checks.append(name)

def assert_core_arrival(page,checks,expect_js=True):
    page.locator('h1').wait_for()
    if expect_js:
        page.wait_for_function("() => document.documentElement.classList.contains('js-ready')")
    record(checks,'01-arrival-h1',page.locator('h1').inner_text().strip()=='Materials-to-Mission Atlas')
    record(checks,'02-60-map-nodes',page.locator('.mineral').count()==60)
    labels=page.locator('.mineral').evaluate_all("els => els.map(e => e.getAttribute('aria-label'))")
    record(checks,'03-60-unique-accessible-names',len(labels)==60 and all(labels) and len(set(labels))==60)
    record(checks,'04-neutral-no-current',page.locator('.mineral[aria-current="true"]').count()==0)
    record(checks,'05-map-list-labels',page.locator('#constellationView').inner_text().strip()=='Map' and page.locator('#indexView').inner_text().strip()=='List')
    record(checks,'06-map-toolbar-visible',page.locator('.map-toolbar').is_visible())
    record(checks,'07-neutral-detail-hidden',not page.locator('#desktopDetail').is_visible())
    record(checks,'08-map-boundary-visible',page.locator('text=Position shows application connection, not ranking.').count()>=1)
    visual=page.evaluate("""() => { const a=getComputedStyle(document.querySelector('.mineral[data-id="gallium"]')); const b=getComputedStyle(document.querySelector('.mineral[data-id="cobalt"]')); return [a.borderColor,a.backgroundImage,a.boxShadow,b.borderColor,b.backgroundImage,b.boxShadow]; }""")
    record(checks,'09-no-gallium-arrival-privilege',visual[:3]==visual[3:])
    no_horizontal_overflow(page); record(checks,'10-no-horizontal-overflow-arrival')
    assert page.locator('.atlas-orientation-line').inner_text().strip() == 'Start with one material. Follow the pathway. See how far the evidence carries. Identify what must be proven next.'
    assert page.locator('.start-here').count() == 0
    guide_text = page.locator('#how-this-map-works').text_content()
    assert guide_text.count('Supported facts stay supported. Unknowns stay visible.') == 1
    assert 'M0 identifies the experimental public evidence method used here. It does not indicate readiness, qualification, certification, or acquisition approval.' in guide_text
    assert page.locator('body').inner_text().count('Reviewed does not mean qualified.') == 1
    assert page.locator('#selected-pathways').inner_text().count('Public evidence is continuous through Gallium; qualified domestic primary recovery remains unresolved.') == 1
    assert page.locator('#selected-pathways').inner_text().count('Public evidence is continuous through critical materials; a qualified material stack remains unresolved.') == 1
    assert page.locator('h1').count() == 1
    assert page.locator('#atlas-title').evaluate("el => el.tagName") == 'H1'
    assert page.locator('.mpi-hero,.mpi-trust-strip,.mpi-pathway-explanation').count() == 0
    assert page.locator('#selected-pathways .selected-pathway-signal').count() == 2
    assert page.locator('#selected-pathways .selected-pathway-preview-meta').count() == 2
    assert page.locator('#selected-pathways .signal-horizon').count() == 2
    assert page.locator('#selected-pathways').inner_text().count('See how far the evidence carries.') == 1
    assert page.locator('#selected-pathways .selected-pathways-legend').count() == 1
    assert page.locator('#selected-pathways .selected-pathways-secondary').count() == 0
    assert page.locator('#selected-pathways').inner_text().count('Experimental public evidence method') == 2
    assert ' '.join(page.locator('#selected-pathways a[href="#ga-pathway"]').inner_text().split()) == 'View Gallium pathway →'
    assert ' '.join(page.locator('#selected-pathways a[href="#yig-pathway"]').inner_text().split()) == 'View YIG pathway →'
    order = page.locator('main > section').evaluate_all("els => els.map(el => el.id || el.className)")
    assert order.index('atlas') < order.index('selected-pathways')
    assert order.index('yig-pathway') < order.index('forms') < order.index('sources')

def assert_mpi_contract(page):
    summaries=page.locator('.mpi-summary')
    assert summaries.count()==2
    ga=page.locator('.mpi-summary[data-mpi-record="GA-001"]')
    yig=page.locator('.mpi-summary[data-mpi-record="YIG-001"]')
    assert ga.count()==1 and yig.count()==1
    assert ga.locator('h3#ga-mpi-title').inner_text().strip()=='What evidence establishes'
    assert yig.locator('h4#yig-mpi-title').inner_text().strip()=='What evidence establishes'
    assert 'CRITICAL MINERAL · REVIEWED PATHWAY · GA-001 v1.0.0 · M0' in ga.inner_text()
    assert 'ENGINEERED MATERIAL SYSTEM · REVIEWED CONTEXT · YIG-001 v1.0.0 · M0' in yig.inner_text()
    assert 'Qualified domestic primary recovery at mission-relevant scale' in ga.locator('[data-mpi-output="evidence-horizon"]').inner_text()
    assert 'Qualified Material Stack' in yig.locator('[data-mpi-output="evidence-horizon"]').inner_text()
    assert all(summary.locator('[data-mpi-output="governing-constraint"]').count()==0 for summary in (ga,yig))
    assert all('Human decision authority remains required.' in summary.locator('.mpi-human-boundary').inner_text() for summary in (ga,yig))
    assert all(summary.locator('aside[aria-label="Human decision boundary"]').count()==1 for summary in (ga,yig))
    assert summaries.locator('dl').count()==2 and summaries.locator('nav[aria-label]').count()==2 and summaries.locator('aside').count()==2
    ribbons=page.locator('.pathway-ribbon')
    assert ribbons.count()==2
    for ribbon in ribbons.all():
        labels=ribbon.locator('li > span').all_text_contents()
        assert labels[0]=='Supported evidence'
        assert 'First unresolved link' in labels and 'Later-stage context' in labels
    assert page.locator('#yig-stages [data-raw-evidence-state="supported-context"] .pathway-stage-state').first.text_content().strip()=='Later-stage context'
    yig_section=page.locator('#yig-pathway')
    assert yig_section.locator('.yig-orientation').count()==1
    assert yig_section.locator('.yig-orientation dt').all_text_contents()==['What it is','Why it matters']
    boundaries=(page.locator('#examine'),page.locator('#yig-boundary'))
    for boundary in boundaries:
        assert boundary.locator('.evidence-boundary-shell').count()==1
        assert boundary.locator('.evidence-findings h3').all_text_contents()==['What We Know',"What We Don't Know"]
        assert boundary.locator('.evidence-findings .state').all_text_contents()==['Supported evidence','Unknown']
        assert boundary.locator('.pathway-boundary-horizon small').text_content().strip()=='Evidence Horizon'
        assert boundary.locator('.pathway-boundary-horizon strong').text_content().strip()=='First unresolved link'
    assert 'Gadolinium gallium garnet (GGG)' in yig_section.inner_text()
    assert 'yttrium scandium gallium aluminum garnet (YSGAG)' in yig_section.inner_text()
    order=page.locator('main').evaluate("main => main.innerHTML")
    ga_steps=['id="ga-pathway"','id="ga-overview"','id="trace"','id="examine"','id="decision"','id="ga-systems"','id="ga-sources"']
    yig_steps=['id="yig-pathway"','id="yig-overview"','id="yig-trace"','id="yig-boundary"','id="yig-next-proof"','id="yig-systems"','id="yig-sources"']
    assert [order.index(step) for step in ga_steps]==sorted(order.index(step) for step in ga_steps)
    assert [order.index(step) for step in yig_steps]==sorted(order.index(step) for step in yig_steps)
    assert page.locator('#gallium > a[href="#ga-overview"]').inner_text().strip().startswith('Explore the Pathway Overview')
    assert page.locator('#ga-overview > a[href="#trace"]').inner_text().strip().startswith('Trace to Mission')
    assert page.locator('#examine .mpi-summary-links a[href="#decision"]').inner_text().strip().startswith('Consider Next Proof')
    assert page.locator('#decision .next-proof-next a[href="#ga-systems"]').inner_text().strip().startswith('Explore Connected Material Systems')
    assert page.locator('#yig-pathway > a[href="#yig-overview"]').inner_text().strip().startswith('Explore the Pathway Overview')
    assert page.locator('#yig-overview > a[href="#yig-trace"]').inner_text().strip().startswith('Trace to Mission')
    assert page.locator('#yig-boundary .mpi-summary-links a[href="#yig-next-proof"]').inner_text().strip().startswith('Consider Next Proof')
    assert page.locator('#yig-next-proof .next-proof-next a[href="#yig-systems"]').inner_text().strip().startswith('Explore Connected Material Systems')
    assert page.locator('.sources-next').count()==0
    rails=page.locator('.pathway-trace-sequence')
    assert rails.count()==2
    assert page.locator('#trace ol.pathway-trace-sequence > li').count()==10
    assert page.locator('#yig-trace ol.pathway-trace-sequence > li').count()==8
    assert page.locator('.pathway-stage').count()==18
    assert page.locator('.pathway-stage[data-presentation-state="supported-evidence"]').count()==2
    assert page.locator('.pathway-stage[data-presentation-state="first-unresolved-link"]').count()==2
    assert page.locator('.pathway-stage[data-presentation-state="later-stage-context"]').count()==6
    assert page.locator('.pathway-stage[data-presentation-state="unresolved-question"]').count()==8
    assert page.locator('#trace [data-stage-id="ga-required-form"][data-raw-evidence-state="supported"] .pathway-stage-state').text_content().strip()=='Later-stage context'
    assert page.locator('#yig-trace [data-stage-id="yig-growth"][data-raw-evidence-state="supported-context"] .pathway-stage-state').text_content().strip()=='Later-stage context'
    assert rails.evaluate_all("els => els.map(el => [el.tagName, el.getAttribute('aria-label'), el.tabIndex])") == [
        ['OL','Gallium trace to mission pathway',0], ['OL','YIG trace to mission pathway',0]
    ]
    rail_layouts=rails.evaluate_all("""els => els.map(el => { const restored=[]; for(let node=el;node;node=node.parentElement){if(getComputedStyle(node).display==='none'){restored.push([node,node.style.display]);node.style.display='block';}} const s=getComputedStyle(el); const tops=[...el.children].map(child => Math.round(child.getBoundingClientRect().top)); const result={flow:s.gridAutoFlow,overflow:s.overflowX,client:el.clientWidth,scroll:el.scrollWidth,tops}; restored.reverse().forEach(([node,display])=>node.style.display=display); return result; })""")
    if page.viewport_size['width']<=720:
        assert all(layout['flow']=='row' and layout['overflow']=='visible' for layout in rail_layouts), rail_layouts
        assert all(layout['tops']==sorted(layout['tops']) and len(set(layout['tops']))==len(layout['tops']) for layout in rail_layouts), rail_layouts
    else:
        assert all(layout['flow']=='column' and layout['overflow']=='auto' for layout in rail_layouts), rail_layouts
        assert all(len(set(layout['tops']))==1 for layout in rail_layouts), rail_layouts
        assert rail_layouts[1]['scroll']>rail_layouts[1]['client'], rail_layouts[1]

def assert_material_system_accessible_names(page):
    buttons=page.locator('#forms .form-card button[data-form-id]')
    assert buttons.count()==10, buttons.count()
    labels=buttons.evaluate_all("els => els.map(e => e.getAttribute(\'aria-label\'))")
    assert len(labels)==10 and all(labels), labels
    assert len(set(labels))==10, labels
    assert all(label.startswith('Open detail: ') for label in labels), labels

def assert_mobile_modal_detail_lifecycle(page,width):
    if width>1160: return
    base=page.url.split('#')[0]
    sheet=page.locator('#materialSheet')
    assert sheet.get_attribute('aria-label')=='Material detail'
    assert sheet.get_attribute('aria-labelledby') is None
    assert page.locator('#sheetTitle').count()==0

    gallium=page.locator('.mineral[data-id="gallium"]')
    gallium.click()
    assert sheet.evaluate("el => el.matches(':modal')")
    assert page.locator('dialog:modal').count()==1
    assert sheet.get_attribute('aria-labelledby')=='sheetTitle'
    assert sheet.locator('#sheetTitle').inner_text().strip()=='Gallium'
    page.evaluate("document.querySelector('#globalSearch').focus()")
    assert sheet.evaluate("el => el.contains(document.activeElement)")
    for _ in range(12):
        page.keyboard.press('Tab')
        assert sheet.evaluate("el => el.contains(document.activeElement) || document.activeElement === document.body")
        assert not page.evaluate("document.activeElement?.matches('#globalSearch, .mineral, .form-card button') === true")
    page.keyboard.press('Escape')
    assert not sheet.evaluate("el => el.matches(':modal')")
    assert gallium.evaluate("el => el === document.activeElement")

    gallium.click()
    page.locator('#sheetClose').click()
    assert not sheet.evaluate("el => el.matches(':modal')")
    assert gallium.evaluate("el => el === document.activeElement")

    yttrium=page.locator('.mineral[data-id="yttrium"]')
    yttrium.click()
    detail=sheet
    yig=detail.locator('[data-form-id="yig"]')
    if not yig.is_visible():
        drawer=yig.locator('xpath=ancestor::details[1]')
        if drawer.get_attribute('open') is None: drawer.locator('summary').click()
        yig.wait_for(state='visible')
    yig.click()
    assert sheet.evaluate("el => el.matches(':modal')")
    assert page.locator('dialog:modal').count()==1
    assert sheet.locator('#sheetTitle').inner_text().strip()=='Yttrium Iron Garnet'
    page.locator('#sheetClose').click()
    assert yttrium.evaluate("el => el === document.activeElement")
    page.goto(base,wait_until='domcontentloaded')

def exercise_search(page,checks):
    search=page.locator('#globalSearch')
    search.fill('Gallium'); search.press('ArrowDown')
    active=search.get_attribute('aria-activedescendant')
    record(checks,'11-search-active-descendant',bool(active) and page.locator('#'+active).count()==1)
    search.press('Escape')
    record(checks,'12-search-escape-clears-active',search.get_attribute('aria-activedescendant') is None)
    search.fill('zzzz-no-public-result-777')
    record(checks,'13-search-no-result',page.locator('#searchResults').inner_text().find('No public result')>=0)
    record(checks,'14-search-no-result-announced','No public result' in page.locator('#experienceStatus').inner_text())
    search.fill('')

def exercise_filter(page,checks):
    btn=page.locator('.lens:not(.all)').first
    btn.click()
    record(checks,'15-filter-active',btn.get_attribute('aria-pressed')=='true')
    record(checks,'16-filter-feedback','of 60' in page.locator('#lensCount').inner_text())
    page.locator('.lens.all').click()
    record(checks,'17-filter-reset','60 minerals' in page.locator('#lensCount').inner_text())

def active_detail(page,width):
    return page.locator('#desktopDetail') if width>1160 else page.locator('#materialSheet')

def exercise_list_and_nonreviewed(page,width,checks):
    page.locator('.mineral[data-id="cobalt"]').click()
    detail=active_detail(page,width)
    record(checks,'18-nonreviewed-no-trace',detail.locator('[data-depth="trace"]').count()==0)
    if width<=1160 and page.locator('#materialSheet').get_attribute('open') is not None:
        page.locator('#sheetClose').click()
    page.locator('#indexView').click()
    record(checks,'19-list-view-active','is-active' in (page.locator('#indexPanel').get_attribute('class') or ''))
    row=page.locator('.index-row[data-index-id="cobalt"]')
    row.locator('summary').click()
    record(checks,'20-list-select-preserves-selection',page.locator('.mineral[data-id="cobalt"]').get_attribute('aria-current')=='true')
    page.locator('#constellationView').click()
    record(checks,'21-map-return-preserves-selection',page.locator('.mineral[data-id="cobalt"]').get_attribute('aria-current')=='true')

def exercise_gallium_proof(page,width,checks):
    page.locator('.mineral[data-id="gallium"]').click()
    detail=active_detail(page,width)
    record(checks,'22-gallium-explore','Gallium' in detail.inner_text())
    action=detail.locator('[data-depth="trace"]'); record(checks,'23-reviewed-trace-door',action.count()>=1)
    if not action.first.is_visible():
        drawer=action.first.locator('xpath=ancestor::details[1]')
        assert drawer.count()==1
        if drawer.get_attribute('open') is None:
            drawer.locator('summary').click()
        action.first.wait_for(state='visible')
    action.first.click(); page.locator('#trace.is-revealed').wait_for()
    if width<=1160:
        assert not page.locator('#materialSheet').evaluate("el => el.matches(':modal')")
    page.locator('#examine.is-revealed').wait_for()
    boundary=page.locator('#examine').inner_text()
    record(checks,'24-boundary-evidence-horizon','evidence horizon' in boundary.lower())
    record(checks,'25-first-unresolved-link','Qualified domestic primary recovery at mission-relevant scale' in boundary)
    record(checks,'26-evidence-boundary-follows-trace',page.locator('#showProof').count()==0 and page.locator('#examine').is_visible())
    record(checks,'27-next-proof-actions',page.locator('#decision .action-card').count()==3)
    record(checks,'28-human-authority-visible','Human decision authority remains required.' in page.locator('#decision').inner_text())
    boundary_copy='This map organizes public evidence and unresolved questions. It does not approve, qualify, or certify a pathway. Decisions requiring judgment remain with responsible people and organizations.'
    assert page.locator('#decision .human-boundary p').inner_text().strip()==boundary_copy
    assert page.locator('#yig-next-proof .human-boundary p').inner_text().strip()==boundary_copy
    assert page.locator('#decision .action-card h3').all_inner_texts()==['Monitor','Validate','Support Next Proof']
    # Natural document flow retains stable hashes for trace and evidence review.
    page.goto(urllib.parse.urljoin(page.url.split('#')[0],'#trace'),wait_until='domcontentloaded')
    page.locator('#trace.is-revealed').wait_for()
    assert page.locator('#examine').is_visible()
    page.goto(urllib.parse.urljoin(page.url.split('#')[0],'#examine'),wait_until='domcontentloaded')
    page.locator('#examine.is-revealed').wait_for()
    record(checks,'29-proof-seven-claims',page.locator('.ga-claim').count()==7)
    claim_register=page.locator('.claim-register')
    assert claim_register.count()==1
    if claim_register.get_attribute('open') is None:
        claim_register.locator('summary').click()
        page.wait_for_function("document.querySelector('.claim-register')?.open === true")
    refs=claim_register.locator('.ga-source-ref')
    assert refs.count()>=7 and refs.first.is_visible()
    record(checks,'30-proof-source-links',refs.count()>=7)
    source_ids=set(refs.evaluate_all("els => els.map(e => e.dataset.gaSourceId)")); record(checks,'31-four-ga-source-identities',len(source_ids)==4)
    payload=json.loads(page.locator('#publicData').text_content())
    raw_sources=payload['ga001']['sources']
    if isinstance(raw_sources, dict):
        raw_sources=raw_sources.get('sources')
    assert isinstance(raw_sources, list) and raw_sources and all(isinstance(s, dict) for s in raw_sources)
    expected={s['source_id']:s['url'] for s in raw_sources}
    record(checks,'32-source-id-set-exact',set(expected)==source_ids)
    for ref in refs.all():
        sid=ref.get_attribute('data-ga-source-id'); href=ref.get_attribute('href'); assert sid in expected and href==f'#ga-source-{sid}' and page.locator(href).count()==1
    for sid in source_ids:
        card=page.locator(f'#ga-source-{sid}'); assert card.count()==1
        href=card.locator('a[target="_blank"]').get_attribute('href'); assert href==expected[sid]
        assert 'wafter' not in card.inner_text().lower() and 'Supports:' in card.inner_text()
    record(checks,'33-source-cards-exact-controlled-urls')
    first=refs.first; sid=first.get_attribute('data-ga-source-id')
    first.scroll_into_view_if_needed()
    assert first.is_visible()
    first.click()
    page.wait_for_function("(sid) => location.hash === '#ga-source-' + sid && document.body.dataset.depth === 'proof'", arg=sid)
    page.locator(f'#ga-source-{sid}').wait_for(state='visible')
    record(checks,'34-source-fragment-keeps-proof',page.evaluate('location.hash').startswith('#ga-source-') and page.locator('#examine').is_visible())
    page.go_back()
    page.wait_for_function("location.hash === '#examine' && document.body.dataset.depth === 'proof'")
    record(checks,'35-history-back-proof',page.locator('#examine').is_visible())
    page.go_back()
    page.wait_for_function("location.hash === '#trace' && document.body.dataset.depth === 'trace'")
    record(checks,'36-history-back-trace',page.locator('#trace').is_visible())
    page.go_forward()
    page.wait_for_function("location.hash === '#examine' && document.body.dataset.depth === 'proof'")
    record(checks,'37-history-forward-proof',page.locator('#examine').is_visible())
    return sorted(source_ids)

def exercise_yig_parent(page,width,checks):
    base=page.url.split('#')[0]
    page.goto(base,wait_until='domcontentloaded')
    page.locator('.mineral[data-id="yttrium"]').click()
    detail=active_detail(page,width)
    yig=detail.locator('[data-form-id="yig"]'); record(checks,'38-yig-discoverable-from-yttrium',yig.count()==1)
    if not yig.is_visible():
        drawer=yig.locator('xpath=ancestor::details[1]')
        assert drawer.count()==1
        if drawer.get_attribute('open') is None:
            drawer.locator('summary').click()
        yig.wait_for(state='visible')
    yig.click(); record(checks,'39-yig-not-critical-mineral','Yttrium Iron Garnet' in detail.inner_text() and 'USGS 2025 Critical Mineral' not in detail.inner_text())
    parent=detail.locator('.parent-link[data-parent-id="yttrium"]'); record(checks,'40-related-system-parent-return',parent.count()==1)
    if not parent.is_visible():
        drawer=parent.locator('xpath=ancestor::details[1]')
        assert drawer.count()==1
        if drawer.get_attribute('open') is None:
            drawer.locator('summary').click()
        parent.wait_for(state='visible')
    parent.click(); record(checks,'41-parent-return-restores-yttrium','Yttrium' in detail.inner_text())

def exercise_legacy_hashes(page,width,checks):
    base=page.url.split('#')[0]
    cases=[
        ('#gallium','detail','Gallium'),
        ('#ga-pathway','#gallium','Gallium'),
        ('#ga-overview','#ga-overview','Pathway Overview'),
        ('#trace','#trace','Trace to Mission'),
        ('#examine','#examine','Evidence Boundary'),
        ('#decision','#decision','Human decision authority remains required.'),
        ('#yig-pathway','#yig-pathway','YIG'),
        ('#yig-overview','#yig-overview','Pathway Overview'),
        ('#ga-sources','#sources','Evidence & Sources'),
        ('#yig-trace','#yig-trace','Trace to Mission'),
        ('#yig-boundary','#yig-boundary','Evidence Boundary'),
        ('#yig-systems','#forms','Connected Material Systems'),
        ('#yig-sources','#sources','Evidence & Sources'),
        ('#yig-next-proof','#yig-next-proof','Next Proof'),
        ('#material-gallium','detail','Gallium'),
        ('#form-yig','detail','Yttrium Iron Garnet'),
    ]
    for h,target,text in cases:
        page.goto(base+h,wait_until='domcontentloaded')
        page.wait_for_function("(hash) => location.hash === hash", arg=h)
        if target == 'detail':
            detail=active_detail(page,width)
            detail.wait_for(state='visible')
            assert text in detail.inner_text()
            if width<=1160:
                assert page.locator('#materialSheet').get_attribute('open') is not None
        else:
            loc=page.locator(target).filter(has_text=text).first
            loc.wait_for(state='visible')
        if h == '#ga-pathway':
            page.wait_for_function("() => document.activeElement?.id === 'gallium-title'")
        if h == '#yig-pathway':
            page.wait_for_function("() => document.activeElement?.id === 'yig-pathway-title'")
        if h == '#ga-sources':
            assert page.locator('.ga-source-card:visible').count()==4
            assert all('ga' in (card.get_attribute('data-pathway-routes') or '').split() for card in page.locator('.source-card:visible').all())
            assert all('ga' in (card.get_attribute('data-pathway-routes') or '').split() for card in page.locator('.form-card:visible').all())
        if h == '#yig-sources':
            assert page.locator('.ga-source-card:visible').count()==0
            assert all('yig' in (card.get_attribute('data-pathway-routes') or '').split() for card in page.locator('.source-card:visible').all())
            assert all('yig' in (card.get_attribute('data-pathway-routes') or '').split() for card in page.locator('.form-card:visible').all())
    record(checks,'42-legacy-and-stable-deep-links')

def assert_csp_and_navigation(page):
    csp=page.locator('meta[http-equiv="Content-Security-Policy"]').get_attribute('content') or ''
    assert "default-src 'none'" in csp and "script-src 'self'" in csp and "connect-src 'none'" in csp
    assert page.locator('a.method-link').get_attribute('href')=='https://github.com/Bridge-Node-7/materials-to-mission'
    footer=page.locator('footer')
    for text in ['Golden Age','Materials-to-Mission','Partner','Privacy','Security','Contact','© 2026 Bridge Node 7']:
        assert text in footer.inner_text()
    continuation=page.locator('.continuation')
    assert continuation.locator('a').count()==2
    assert continuation.locator('a').nth(0).get_attribute('href')=='https://bridgenode7.com/frontier-decision-engine/start.html'
    assert continuation.locator('a').nth(1).get_attribute('href')=='https://bridgenode7.com/partner/'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base-url',required=True); ap.add_argument('--evidence',required=True); args=ap.parse_args()
    out=Path(args.evidence); out.mkdir(parents=True,exist_ok=True); results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for width,height in VIEWPORTS:
            checks=[]; errors=[]
            context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
            page=context.new_page(); page.on('console',lambda m: errors.append(f'console:{m.type}:{m.text}') if m.type=='error' else None); page.on('pageerror',lambda e: errors.append(f'pageerror:{e}'))
            page.goto(args.base_url,wait_until='networkidle',timeout=60000)
            assert_core_arrival(page,checks); assert_mpi_contract(page); assert_material_system_accessible_names(page); assert_mobile_modal_detail_lifecycle(page,width); exercise_search(page,checks); exercise_filter(page,checks); exercise_list_and_nonreviewed(page,width,checks); sources=exercise_gallium_proof(page,width,checks); exercise_yig_parent(page,width,checks); exercise_legacy_hashes(page,width,checks); assert_csp_and_navigation(page)
            no_horizontal_overflow(page)
            assert len(set(checks))==42, (len(checks),checks)
            if errors: raise AssertionError(errors)
            shot=out/f'viewport-{width}x{height}.png'; page.screenshot(path=str(shot),full_page=True)
            results.append({'profile':'42-contract','viewport':[width,height],'status':'PASS','checks':checks,'sources':sources,'screenshot':shot.name})
            context.close()

        # Focus visibility
        context=browser.new_context(viewport={'width':1280,'height':720}); page=context.new_page(); errs=[]; page.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); page.on('pageerror',lambda e: errs.append(str(e))); page.goto(args.base_url,wait_until='networkidle',timeout=60000); tab_to_id(page,'globalSearch'); focus_is_visible(page); tab_to_selector(page,'.mineral'); focus_is_visible(page); assert page.evaluate("document.activeElement?.classList.contains('mineral') === true"); assert not errs; page.screenshot(path=str(out/'focus-visible.png'),full_page=True); results.append({'profile':'focus-visible','status':'PASS'}); context.close()
        # Forced colors
        context=browser.new_context(viewport={'width':1280,'height':720},forced_colors='active',reduced_motion='reduce'); page=context.new_page(); page.goto(args.base_url,wait_until='networkidle',timeout=60000); checks=[]; assert_core_arrival(page,checks); assert_mpi_contract(page); tab_to_selector(page,'.mineral'); focus_is_visible(page); focused_id=page.evaluate("document.activeElement?.dataset?.id"); assert focused_id; page.keyboard.press('Enter'); assert page.locator(f'.mineral[data-id="{focused_id}"][aria-current="true"]').count()==1; page.screenshot(path=str(out/'forced-colors.png'),full_page=True); results.append({'profile':'forced-colors','status':'PASS'}); context.close()
        # 200%-equivalent reflow
        context=browser.new_context(viewport={'width':640,'height':900},reduced_motion='reduce'); page=context.new_page(); page.goto(args.base_url,wait_until='networkidle',timeout=60000); checks=[]; assert_core_arrival(page,checks); no_horizontal_overflow(page); page.screenshot(path=str(out/'zoom-200-equivalent-reflow.png'),full_page=True); results.append({'profile':'zoom-200-equivalent-reflow','status':'PASS'}); context.close()
        # Mobile touch
        context=browser.new_context(viewport={'width':375,'height':812},is_mobile=True,has_touch=True,reduced_motion='reduce'); page=context.new_page(); page.goto(args.base_url,wait_until='networkidle',timeout=60000); checks=[]; assert_core_arrival(page,checks); page.locator('.mineral[data-id="gallium"]').tap(); sheet=page.locator('#materialSheet'); assert sheet.evaluate("el => el.matches(':modal')") and 'Gallium' in sheet.inner_text(); results.append({'profile':'mobile-touch','status':'PASS'}); context.close()
        # Grayscale / non-color selected state
        context=browser.new_context(viewport={'width':1280,'height':720},reduced_motion='reduce'); page=context.new_page(); page.goto(args.base_url,wait_until='networkidle',timeout=60000); page.wait_for_function("() => document.documentElement.classList.contains('js-ready')"); page.evaluate("document.documentElement.style.filter='grayscale(1)'"); gallium=page.locator('.mineral[data-id="gallium"]'); cobalt=page.locator('.mineral[data-id="cobalt"]'); gallium.click(); assert gallium.get_attribute('aria-current')=='true'; assert 'selected' in (gallium.get_attribute('class') or '').split(); page.wait_for_function("""() => {const ga=document.querySelector('.mineral[data-id="gallium"]'); const co=document.querySelector('.mineral[data-id="cobalt"]'); if(!ga||!co) return false; const a=new DOMMatrixReadOnly(getComputedStyle(ga).transform); const b=new DOMMatrixReadOnly(getComputedStyle(co).transform); return Math.abs(a.a-b.a)>.15;}""",timeout=3000); state=page.evaluate("""() => {const ga=document.querySelector('.mineral[data-id="gallium"]'); const co=document.querySelector('.mineral[data-id="cobalt"]'); const a=getComputedStyle(ga); const b=getComputedStyle(co); const aspan=getComputedStyle(ga.querySelector('span')); const bspan=getComputedStyle(co.querySelector('span')); return {selected:{transform:a.transform,borderWidth:a.borderWidth,fontSize:aspan.fontSize},peer:{transform:b.transform,borderWidth:b.borderWidth,fontSize:bspan.fontSize}};}"""); assert state['selected']['borderWidth']!=state['peer']['borderWidth'], state; assert state['selected']['transform']!=state['peer']['transform'], state; assert state['selected']['fontSize']!=state['peer']['fontSize'], state; results.append({'profile':'grayscale-noncolor-state','status':'PASS','state':state}); context.close()
        # Programmatic reduced-motion behavior
        context=browser.new_context(viewport={'width':1280,'height':720},reduced_motion='reduce')
        context.add_init_script("window.__m2mScrollBehaviors = []; const __m2mOriginalScrollIntoView = Element.prototype.scrollIntoView; Element.prototype.scrollIntoView = function(options) { if (options && typeof options === 'object') window.__m2mScrollBehaviors.push(options.behavior || null); return __m2mOriginalScrollIntoView.call(this, options); };")
        page=context.new_page(); page.goto(args.base_url,wait_until='networkidle',timeout=60000)
        page.wait_for_function("() => document.documentElement.classList.contains('js-ready')")
        page.wait_for_function("Array.isArray(window.__m2mScrollBehaviors)")
        page.locator('.mineral[data-id=\"gallium\"]').click()
        special_trace=page.locator('#desktopDetail [data-depth=\"trace\"]')
        if not special_trace.is_visible():
            drawer=special_trace.locator('xpath=ancestor::details[1]')
            assert drawer.count()==1
            if drawer.get_attribute('open') is None:
                drawer.locator('summary').click()
            special_trace.wait_for(state='visible')
        special_trace.click()
        page.wait_for_function("document.body.dataset.depth === 'trace'")
        page.wait_for_timeout(100)
        behaviors=page.evaluate("window.__m2mScrollBehaviors")
        assert behaviors and set(behaviors)=={'auto'}, behaviors
        results.append({'profile':'reduced-motion-programmatic-scroll','status':'PASS','behaviors':behaviors})
        context.close()
        # No JS evidence contract
        context=browser.new_context(viewport={'width':375,'height':812},java_script_enabled=False); page=context.new_page(); page.goto(args.base_url,wait_until='domcontentloaded',timeout=60000); assert page.locator('h1').inner_text().strip()=='Materials-to-Mission Atlas'; assert page.locator('.mineral').count()==60; assert page.locator('.selected-pathway-row').count()==len(SELECTED_PATHWAYS); assert all(page.locator(f'.selected-pathway-row[data-pathway="{item["source_id"]}"]').count()==1 for item in SELECTED_PATHWAYS); assert page.locator('.ga-claim').count()==7; assert page.locator('.ga-source-card').count()==4; assert_mpi_contract(page); assert_csp_and_navigation(page); no_horizontal_overflow(page); results.append({'profile':'no-js','status':'PASS'}); context.close()
        browser.close()
    expected_profiles=len(VIEWPORTS)+7
    assert len(results)==expected_profiles, (len(results),expected_profiles)
    (out/'browser-uat.json').write_text(json.dumps({'status':'PASS','results':results,'release_gate':'A1-A9 plus automated browser/accessibility contract','human_device_at_attestation':'OPEN_NOT_ASSERTED'},indent=2)+'\n',encoding='utf-8')
    print(f'PASS - browser UAT {len(results)} profiles; 42-contract exercised at {len(VIEWPORTS)} viewports')
    return 0
if __name__=='__main__': raise SystemExit(main())
