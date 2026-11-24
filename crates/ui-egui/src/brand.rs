//! The app's mark. PatroneOS edition: this modified version may not show the ArtCraft marks
//! (docs/brand/LICENSE-brand.txt), so it shows its own app icon instead. The pictures come from the framework's SVG
//! source, which bounds the decode and draws nothing for bytes it cannot read.

use craft::ui::contract::Show as _;
use craft::ui::display::{Picture, PictureSize};

const MARK: &[u8] = include_bytes!("../../../assets/app-icon/pdfcraft.svg");

/// The square app mark at `size`.
pub(crate) fn mark(ui: &mut egui::Ui, size: PictureSize) {
    let _ = Picture::svg("PdfCraft".to_string(), MARK).extent(size).show(ui);
}
