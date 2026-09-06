from torch.utils.data import DataLoader
from src.extract_annotations import generate_unified_json
from src.dataloader import SkyFindStreamingDataset
from src.config import BATCH_SIZE

def run_pipeline():
    print("=== Step 1: Executing Unified Annotation Extraction ===")
    generate_unified_json()

    print("\n=== Step 2: Validating Multimodal Data Loader ===")
    dataset = SkyFindStreamingDataset()

    # batch_size=None because we yield complete structural dictionaries
    loader = DataLoader(dataset, batch_size=None)

    for i, batch in enumerate(loader):
        print(f"\n[SUCCESS] Loaded Batch Item {i+1}")
        print(f"-> File Name: {batch['file_name']}")
        print(f"-> Image Type: {type(batch['image'])}")
        print(f"-> Bounding Boxes / Entities Found: {len(batch['grounding_data'])}")

        if len(batch['grounding_data']) > 0:
            print(f"-> Sample Expression: {batch['grounding_data'][0]['expressions'][0]}")

        if i + 1 >= BATCH_SIZE:
            break

    print("\n=== Pipeline execution fully completed without errors ===")

if __name__ == "__main__":
    run_pipeline()