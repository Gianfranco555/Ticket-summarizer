"""Command-line interface for the ticket summarizer."""

import argparse
import asyncio
from pathlib import Path

from summarizer import (
    aggregator,
    chunker,
    config,
    loader,
    writer,
    llm_client,
)


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Summarize support tickets.")
    parser.add_argument("csv_in", type=Path, help="Path to the input CSV file.")
    parser.add_argument("--out", type=Path, help="Path to the output CSV file.")
    parser.add_argument("--markdown", type=Path, help="Path to the output Markdown file.")
    parser.add_argument("--model", type=str, help="Name of the LLM model to use.")
    parser.add_argument("--chunk-size", type=int, help="Chunk size in tokens.")
    parser.add_argument("--overlap", type=int, help="Chunk overlap in tokens.")
    return parser.parse_args()


async def main() -> None:
    """Main function for the summarizer CLI."""
    args = _parse_args()

    # Override settings with CLI arguments if provided
    if args.model:
        config.settings.model = args.model
    if args.chunk_size:
        config.settings.chunk_max_tokens = args.chunk_size
    if args.overlap:
        config.settings.chunk_overlap = args.overlap

    # 1. Load tickets
    tickets = loader.load_tickets(args.csv_in, delimiter=config.settings.csv_delimiter)

    # 2. Chunk tickets
    chunks = chunker.chunk_tickets(
        tickets,
        chunk_max_tokens=config.settings.chunk_max_tokens,
        overlap=config.settings.chunk_overlap,
    )

    # 3. Call the LLM for each chunk concurrently
    tasks = [llm_client.summarise_chunk(chunk) for chunk in chunks]
    chunk_results = await asyncio.gather(*tasks)

    # 4. Merge & order results
    rows = aggregator.merge_results(chunk_results)

    # 5. Write outputs
    if args.out:
        writer.write_csv(rows, args.out)
    if args.markdown:
        writer.write_markdown(rows, args.markdown)

if __name__ == "__main__":
    asyncio.run(main())
