import re
from enum import Enum


class ProgressStatusEnum(str, Enum):
    STARTED = "started"
    DOWNLOADING = "downloading"
    FINISHED = "finished"
    DOWNLOADED = "downloaded"  # by client
    DELETED = "deleted"


class MediaFormatOptions(str, Enum):
    # Video formats
    MP4 = "mp4"
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"

    @property
    def is_audio(self) -> bool:
        return self.name in [MediaFormatOptions.MP3, MediaFormatOptions.WAV]


YOUTUBE_URI_REGEX = re.compile(
    r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)
