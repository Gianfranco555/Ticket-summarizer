import argparse
from summarizer import (
    loader,
    chunker,
    llm_client,
    aggregator,
    writer,
    config,
)

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Zscaler support tickets.")
    parser.add_argument("csv_in", help="The input CSV file.")
    parser.add_argument("--out", help="The output CSV file.", default="summary.csv")
    parser.add_argument("--markdown", help="The output markdown file.", default="summary.md")
    parser.add_argument("--model", help="The LLM model to use.")
    parser.add_argument("--chunk-size", type=int, help="The chunk size in tokens.")
    parser.add_argument("--overlap", type=int, help="The chunk overlap in tokens.")
    return parser.parse_args()

def main() -> None:
    args = _parse_args()

    # Override settings with CLI arguments if provided
    if args.model:
        config.settings.llm_model = args.model
    if args.chunk_size:
        config.settings.max_tokens = args.chunk_size
    if args.overlap:
        config.settings.chunk_overlap = args.overlap

    # 2-A  Load tickets
    tickets = loader.load_tickets(args.csv_in)

    # 2-B  Chunk tickets with token awareness
    chunks = chunker.chunk_tickets(
        tickets,
        max_tokens=config.settings.max_tokens,
        overlap=config.settings.chunk_overlap,
    )

    # 2-C  Call the LLM for each chunk
    chunk_results: list[list[dict]] = []
    for chunk in chunks:
        summaries = llm_client.summarise_chunk_sync(chunk)
        chunk_results.append(summaries)

    # 2-D  Merge & order results
    rows = aggregator.merge_results(chunk_results)

    # 2-E  Write outputs
    writer.write_csv(rows, args.out)
    writer.write_markdown(rows, args.markdown)

if __name__ == "__main__":
    main()
