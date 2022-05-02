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
    keep: bool = True
    width: int = 1146
    height: int = 717
    padding: bool = True

    def __post_init__(self):
        self.set_logger()
        output = Path(self.output)
        if output.exists() and not self.force:
            raise LoggedError(self.log, "%s already exists", self.output)
        if not self.keep and self.padding:
            self.log.warning("Padding is not supported when keep is False")
            self.padding = False

    def load(self) -> Image.Image:
        try:
            with Image.open(self.file) as image:
                image.convert('RGB')
        except OSError as err:
            raise LoggedError(
                self.log, "%s is not a valid image file", self.file) from err
        return image

    def resize(
        self,
        image: Image.Image,
        refwidth: int = 1146, refheight: int = 717,
    ) -> Image.Image:
        if self.keep:
            width, height = image.size
            ratio = width / height
            cwidth, cheight = refwidth / width, refheight / height
            if not self.padding:
                if cwidth > cheight:
                    newsize = (int(width * cwidth),
                               int(width * cwidth / ratio))
                else:
                    newsize = (int(height * cheight * ratio),
                               int(height * cheight))
                newimage = image.resize(newsize, Image.LANCZOS)
            else:
                if cwidth > cheight:
                    newsize = (int(height * cheight * ratio),
                               int(height * cheight))
                    box = ((refwidth - newsize[0]) // 2, 0)
                else:
                    newsize = (int(width * cwidth),
                               int(width * cwidth / ratio))
                    box = (0, (refheight - newsize[1]) // 2)
                resized = image.resize(newsize, Image.LANCZOS)
                newimage = Image.new('RGB', (refwidth, refheight), (0, 0, 0))
                newimage.paste(resized, box)
        else:
            newsize = (refwidth, refheight)
            newimage = image.resize(newsize, Image.LANCZOS)

        return newimage

    def run(self) -> None:
        image = self.load()
        image = self.resize(image, self.width, self.height)
        image.save(self.output, self.extension)
