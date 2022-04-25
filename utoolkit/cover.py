from dataclasses import dataclass
from pathlib import Path
from PIL import Image
from utoolkit.log import HasLogger
from utoolkit.log import LoggedError


@dataclass
class Cover(HasLogger):
    file: str
    output: str = "cover.jpg"
    force: bool = False
    extension: str = "jpeg"

    def __post_init__(self):
        self.set_logger()
        output = Path(self.output)
        if output.exists() and not self.force:
            raise LoggedError(self.log, "%s already exists", self.output)

    def load(self) -> Image.Image:
        try:
            with Image.open(self.file) as image:
                image.convert('RGB')
        except OSError as err:
            raise LoggedError(
                self.log, "%s is not a valid image file", self.file) from err
        return image

    def resize(self, refwidth: int = 1146, refheight: int = 717) -> Image.Image:
        image = self.load()

        width, height = image.size
        ratio = width / height
        cwidth, cheight = refwidth / width, refheight / height
        if cwidth > cheight:
            newsize = (int(width * cwidth), int(width * cwidth / ratio))
        else:
            newsize = (int(height * cheight * ratio), int(height * cheight))
        image = image.resize(newsize, Image.LANCZOS)

        return image

    def run(self) -> None:
        image = self.resize()
        image.save(self.output, self.extension)
