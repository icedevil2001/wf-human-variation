#!/usr/bin/env python
"""Report using ezcharts."""
import os

from ezcharts.components.fastcat import SeqSummary
from ezcharts.components.reports import labs
import pandas as pd

from .report_utils import read_data, sections  # noqa: ABS101

from .util import get_named_logger, wf_parser  # noqa: ABS101


def main(args):
    """Run entry point."""
    logger = get_named_logger("report")

    # read input stats data
    stats_df = read_data.bamstats(args.stats_dir)

    # read input flagstats data
    flagstat_df = read_data.flagstat(args.flagstat_dir)

    # Define categories
    sample_names = stats_df["sample_name"].cat.categories
    if sample_names != sample_names:
        raise ValueError('Sample names in the two stats file do not match')

    # create the report
    report = labs.LabsReport(
        f"{args.name} reads QC report",
        args.name,
        args.params,
        args.versions,
    )

    # Add summary table of the input flagstats
    sections.summary(report, sample_names, stats_df, flagstat_df)

    # Combine multiple input files
    infiles = pd.concat([
        pd.read_csv(f"{args.stats_dir}/{x}", sep='\t')
        for x in os.listdir(args.stats_dir)])
    with report.add_section("Read statistics", "Stats"):
        SeqSummary(infiles)

    # extract the mapped reads and some other metrics used in the report sections
    stats_df_mapped = stats_df.query('ref != "*"')
    sections.mapping(report, stats_df_mapped)

    # write the report to the output file
    report_fname = f"{args.name}-alignment-report.html"
    report.write(report_fname)

    logger.info(f"Written report to '{report_fname}'.")


def argparser():
    """Argument parser for entrypoint."""
    parser = wf_parser("report")
    parser.add_argument(
        "--name",
        help="report name",
    )
    parser.add_argument(
        "--stats_dir",
        help="directory with `bamstats` per-read stats for the sample",
    )
    parser.add_argument(
        "--flagstat_dir",
        help="directory with `bamstats` per-file stats",
    )
    parser.add_argument(
        "--refnames_dir",
        help="directory with files containing reference names",
    )
    parser.add_argument(
        "--params",
        default=None,
        help="CSV file with workflow parameters",
    )
    parser.add_argument(
        "--versions",
        help="CSV file with software versions",
    )
    return parser