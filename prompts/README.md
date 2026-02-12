# Prompt composition

Prompt sources are split into composable text files:

- `system_base.txt`: core safety rules and strict ACTION JSON protocol.
- `traits/arya_traits.txt`: Arya communication style and emotion mirroring.
- `modes/*.txt`: optional additive mode files (example: `modes/unhinged.txt`).

## Composition order

`build_system_prompt(mode)` composes in this order:
1. `system_base.txt`
2. `traits/arya_traits.txt`
3. optional `modes/{mode}.txt` (if mode is provided and file exists)

## Editing policy

- `system_base.txt` is foundational and should not be rewritten after initial creation.
- Future trait changes must be **append-only** in `traits/arya_traits.txt` (no reorder/delete/reformat of existing lines).
- Modes should be additive and isolated in `modes/` files.
