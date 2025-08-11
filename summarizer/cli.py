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
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="A CLI tool to parse, chunk, and summarize Zscaler help-desk tickets using an LLM."
    )
    parser.add_argument("csv_in", help="The path to the input CSV file.")
    parser.add_argument(
        "--out",
        help="The path to the output CSV file.",
    )
    parser.add_argument(
        "--markdown",
        help="The path to the output Markdown file.",
    )
    parser.add_argument(
        "--model",
        help="The OpenAI model to use for summarization.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="The maximum number of tokens per chunk.",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        help="The number of tokens to overlap between chunks.",
    )
    return parser.parse_args()

def main() -> None:
    args = _parse_args()

    # Load tickets
    tickets = loader.load_tickets(args.csv_in)

    # Chunk tickets with token awareness
    chunks = chunker.chunk_tickets(
        tickets,
        max_tokens=args.chunk_size or config.settings.max_tokens,
        overlap=args.overlap or config.settings.chunk_overlap,
    )

    # Call the LLM for each chunk
    chunk_results: list[list[dict]] = []
    for chunk in chunks:
        summaries = llm_client.summarise_chunk_sync(chunk)
        chunk_results.append(summaries)

    # Merge & order results
    rows = aggregator.merge_results(chunk_results)

    # Write outputs
    if args.out:
        writer.write_csv(rows, args.out)
    if args.markdown:
        writer.write_markdown(rows, args.markdown)


if __name__ == "__main__":
    main()
