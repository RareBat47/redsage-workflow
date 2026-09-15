# Nested Git history handling

"
        "Git internals were intentionally not copied into the outer migration repository.

"
        "- The complete checked-out RedSage v2 working tree, including collected local modifications and untracked files, is under `RedSage_v2/`.
"
        "- The collection-time Git status and remote are under `verification/RedSage_v2_git_status.txt`.
"
        "- Portable RedSage v2 Git refs/history are in `RedSage_v2.git.bundle`; verify with `git bundle verify RedSage_v2.git.bundle`.
"
        "- Nested `.git` directories from staged third-party resources were excluded. Their checked-out source/resource content remains.
"
        "- The temporary ASVS nested pack `RESOURCES/.../asvs/.git/objects/pack/tmp_pack_dckse7` was excluded.
"
        