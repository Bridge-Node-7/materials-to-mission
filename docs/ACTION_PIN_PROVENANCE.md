# GitHub Action Pin Provenance

The release baseline pins every third-party Action to a full commit SHA.

| Action | Release | Full commit SHA | Upstream |
|---|---:|---|---|
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `https://github.com/actions/checkout/releases/tag/v7.0.1` |
| `actions/setup-python` | `v7.0.0` | `5fda3b95a4ea91299a34e894583c3862153e4b97` | `https://github.com/actions/setup-python/releases/tag/v7.0.0` |
| `actions/upload-artifact` | `v7.0.1` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | `https://github.com/actions/upload-artifact/releases/tag/v7.0.1` |
| `github/codeql-action` | `v4.37.6` | `5595ccaf912efad79be6eef63a5619ff05969be3` | `https://github.com/github/codeql-action/releases/tag/v4.37.6` |
| `actions/configure-pages` | `v6.0.0` | `45bfe0192ca1faeb007ade9deae92b16b8254a0d` | `https://github.com/actions/configure-pages/releases/tag/v6.0.0` |
| `actions/upload-pages-artifact` | `v5.0.0` | `fc324d3547104276b827a68afc52ff2a11cc49c9` | `https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0` |
| `actions/deploy-pages` | `v5.0.0` | `cd2ce8fcbc39b97be8ca5fce6e763baed58fa128` | `https://github.com/actions/deploy-pages/releases/tag/v5.0.0` |

A release tag or branch name is not used as the executable reference. Pin updates require
upstream provenance review, complete local validation, and a new reviewed repository identity.
