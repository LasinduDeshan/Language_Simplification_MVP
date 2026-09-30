"""Step 1A: Register candidate external English dataset sources in pending initial states."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.datasets.external_english.registry import ExternalDatasetRegistry
from app.datasets.external_english.schemas import (
    DatasetPermissions,
    ExternalDatasetRegistryRecord,
)


def main():
    print("Registering candidate external English datasets in registry...")
    registry = ExternalDatasetRegistry()

    # 1. ASSET (Alva-Manchego et al., ACL 2020)
    asset_record = ExternalDatasetRegistryRecord(
        dataset_id="EXTDATA-ASSET",
        dataset_name="ASSET",
        official_source_url="https://github.com/facebookresearch/asset",
        publication_reference="Alva-Manchego, F., Martin, L., Bordes, A., Scarton, C., Sagot, B., & Specia, L. (2020). ASSET: A Dataset for Tuning and Evaluation of Sentence Simplification Models with Multiple Rewriting Transformations. In Proceedings of ACL 2020 (pp. 4668–4679).",
        content_licence_name=None,
        content_licence_url=None,
        repository_code_licence="CC-BY-NC-4.0",
        source_text_licence=None,
        crowdsourced_references_licence=None,
        dataset_collection_terms=None,
        rights_status="pending_content_rights_verification",
        permissions=DatasetPermissions(),
        evidence=None,
        notes="Primary multi-reference evaluation benchmark for sentence simplification.",
    )
    registry.register(asset_record)

    # 2. TurkCorpus (Xu et al., TACL 2016)
    turk_record = ExternalDatasetRegistryRecord(
        dataset_id="EXTDATA-TURKCORPUS",
        dataset_name="TurkCorpus",
        official_source_url="https://github.com/cocoxu/simplification",
        publication_reference="Xu, W., Callison-Burch, C., & Napoles, C. (2016). Optimizing statistical machine translation for text simplification. Transactions of the Association for Computational Linguistics, 4, 401–415.",
        content_licence_name=None,
        content_licence_url=None,
        repository_code_licence="GPL-3.0",
        source_text_licence=None,
        crowdsourced_references_licence=None,
        dataset_collection_terms=None,
        rights_status="pending_content_rights_verification",
        permissions=DatasetPermissions(),
        evidence=None,
        notes="Standard SARI-compatible evaluation benchmark sharing source sentences with ASSET.",
    )
    registry.register(turk_record)

    # 3. OasisSimp-English (De Silva et al., 2024)
    oasissimp_record = ExternalDatasetRegistryRecord(
        dataset_id="EXTDATA-OASISSIMP-EN",
        dataset_name="OasisSimp-English",
        official_source_url="https://OasisSimpDataset.github.io/",
        publication_reference="De Silva, N. et al. (2024). OasisSimp: Multilingual Sentence Simplification Dataset and Benchmarks.",
        content_licence_name=None,
        content_licence_url=None,
        repository_code_licence=None,
        source_text_licence=None,
        crowdsourced_references_licence=None,
        dataset_collection_terms=None,
        rights_status="pending_content_rights_verification",
        permissions=DatasetPermissions(),
        evidence=None,
        notes="Multilingual sentence simplification dataset; English split serves as cross-domain benchmark.",
    )
    registry.register(oasissimp_record)

    # 4. WikiLarge Pilot (Zhang & Lapata, EMNLP 2017)
    wikilarge_record = ExternalDatasetRegistryRecord(
        dataset_id="EXTDATA-WIKILARGE-PILOT",
        dataset_name="WikiLarge Pilot",
        official_source_url="https://github.com/XingxingZhang/dress",
        publication_reference="Zhang, X., & Lapata, M. (2017). Sentence Simplification with Deep Reinforcement Learning. In Proceedings of EMNLP 2017 (pp. 584–594).",
        content_licence_name=None,
        content_licence_url=None,
        repository_code_licence="MIT",
        source_text_licence="CC-BY-SA 3.0 (Wikipedia Lineage)",
        crowdsourced_references_licence=None,
        dataset_collection_terms=None,
        rights_status="pending_lineage_and_rights_verification",
        permissions=DatasetPermissions(),
        evidence=None,
        notes="Wikipedia sentence alignments for large-scale training reference; optional filtered pilot only.",
    )
    registry.register(wikilarge_record)

    # 5. Newsela (Xu et al., 2015)
    newsela_record = ExternalDatasetRegistryRecord(
        dataset_id="EXTDATA-NEWSELA",
        dataset_name="Newsela",
        official_source_url="https://newsela.com/data/",
        publication_reference="Xu, W., Callison-Burch, C., & Napoles, C. (2015). Problems in Current Text Simplification Research: New Data Can Help. TACL.",
        content_licence_name="Proprietary / Restricted Research Agreement",
        content_licence_url=None,
        repository_code_licence=None,
        source_text_licence=None,
        crowdsourced_references_licence=None,
        dataset_collection_terms=None,
        rights_status="excluded_rights",
        permissions=DatasetPermissions(),
        evidence=None,
        notes="Proprietary news simplification corpus; formally excluded without written license agreement.",
    )
    registry.register(newsela_record)

    registry.save()
    print(f"Successfully registered {len(registry.list_all())} datasets in {registry.registry_file}")


if __name__ == "__main__":
    main()
