# PdfCraft, PatroneOS edition

<img src="../assets/app-icon/pdfcraft-small.svg" alt="" width="96">

A fork of [PdfCraft](https://github.com/storytold/pdfcraft) by the ArtCraft team, kept up to date with it,
with three changes for [PatroneOS](https://patroneos.com):

- **PatroneOS fonts.** The interface is drawn in PatroneOS Sans (Regular, and SemiBold for medium and
  semibold text) and PatroneOS Mono, from [patroneos-fonts](https://github.com/billsecond/patroneos-fonts)
  1.1.0 (`assets/fonts/patroneos`, SIL Open Font License 1.1). Inter and JetBrains Mono stay behind them in
  every font family, for the letters the PatroneOS fonts don't have (Cyrillic, Greek and other scripts).
  Text that PdfCraft writes into PDFs (edits, signatures, demo pages) still uses Inter, which covers those
  scripts. The change is in `crates/ui-egui/src/fonts.rs`.
- **A new app icon.** A page being signed with a fountain pen, in the style of PatroneOS's icons, with a
  simpler drawing for 16-32 px. See [assets/app-icon/README.md](../assets/app-icon/README.md);
  [icons.py](icons.py) renders every size.
- **No ArtCraft marks.** The ArtCraft brand licence (`docs/brand/LICENSE-brand.txt`) doesn't allow a modified
  version to show them, so the About dialog and the home screen show this edition's own icon, and the About
  dialog says it is based on PdfCraft by the ArtCraft team.

## Staying up to date

`.github/workflows/patrone-update-from-upstream.yml` checks the original every day. When it has new changes, it
opens a pull request, "Update from the original PdfCraft", which keeps updating itself until it's merged.
Merge it with **Create a merge commit**. It needs, once, in this repository's Settings > Actions > General:
Actions allowed, and "Allow GitHub Actions to create and approve pull requests" ticked.

The fork's changes are kept small and in few places, so most updates merge cleanly. When one doesn't, the
pull request says how to resolve it.

To update by hand instead, in a clone with the original as `upstream`
(`git remote add upstream https://github.com/storytold/pdfcraft.git`):

```
git fetch upstream
git switch -c update/upstream origin/main
git merge upstream/main
```

then push the branch and open a pull request.
