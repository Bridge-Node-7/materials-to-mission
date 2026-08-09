# Final GitHub Public Release Plan

1. Verify the exact final source archive, manifest, commit, tree, and Git bundle.
2. Confirm the authenticated personal GitHub account is `Bridge-Node-7` and the target
   repository does not exist.
3. Create the public repository and push only the exact prebuilt `main` commit.
4. Verify CI and CodeQL for that exact commit.
5. Configure metadata, private vulnerability reporting, and immutable releases separately.
6. Verify signing readiness; create, verify, and push one signed annotated `v0.1.0` tag.
7. Allow the tag-triggered Release workflow to create the immutable release and assets.
8. Perform complete public readback, asset download, checksum verification, and Latest check.
9. Apply a minimal website-linkage patch in a separate website branch and release.
10. Consider an FDE adapter only after the canonical release and website readback.

Each consequential write requires a separate reviewed authorization. The source repository
contains no executable public-write gate.
