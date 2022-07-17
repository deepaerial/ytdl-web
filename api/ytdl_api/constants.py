import re
from enum import Enum


class DownloaderTypes(str, Enum):
    PYTUBE = "pytube"
    MOCK = "mocked"

    def __str__(self) -> str:
        return self.value


class ProgressStatusEnum(str, Enum):
    CREATED = "created"
    STARTED = "started"
    DOWNLOADING = "downloading"
    FINISHED = "finished"
    DOWNLOADED = "downloaded"  # by client
    DELETED = "deleted"

    def __str__(self) -> str:
        return self.value


class MediaFormat(str, Enum):
    # Video formats
    MP4 = "mp4"
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"

    @property
    def is_audio(self) -> bool:
        return self.name in [MediaFormat.MP3, MediaFormat.WAV]

    def __str__(self) -> str:
        return self.value


YOUTUBE_URI_REGEX = re.compile(
    r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)
