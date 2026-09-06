from torch.utils.data import IterableDataset
from datasets import load_dataset
from PIL import ImageFile

from src.config import DATASET_NAME, SPLIT, OUTPUT_JSON
from src.utils import load_json

ImageFile.LOAD_TRUNCATED_IMAGES = True


class SkyFindStreamingDataset(IterableDataset):

    def __init__(self):
        super().__init__()

        annotations = load_json(OUTPUT_JSON)

        self.annotation_map = {
            item["fileName"]: item["annotations"]
            for item in annotations
        }

    def _stream_generator(self):

        hf_stream = load_dataset(
            DATASET_NAME,
            split=SPLIT,
            streaming=True
        )

        for idx, record in enumerate(hf_stream):

            file_name = record["fileName"]

            yield {
                "file_name": file_name,
                "grounding_data": self.annotation_map.get(
                    file_name,
                    []
                )
            }

            if (idx + 1) % 1000 == 0:
                print(
                    f"[INFO] Streamed {idx + 1:,} samples"
                )

    def __iter__(self):
        return self._stream_generator()