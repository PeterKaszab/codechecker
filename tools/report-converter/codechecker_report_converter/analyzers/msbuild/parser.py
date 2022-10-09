# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------

import logging
import os
import re

from typing import Iterator, List, Tuple

from codechecker_report_converter.report import get_or_create_file, Report
from ..parser import BaseParser


LOG = logging.getLogger('report-converter')


class Parser(BaseParser):
    """
    Parser for MSBuild Output
    """

    def __init__(self, analyzer_result):
        super(Parser, self).__init__()

        self.analyzer_result = analyzer_result

        self.message_line_re = re.compile(
            # Message prefix followed by a '>'.
            r"^(?P<prefix>[:\d]+)>"
            # Path followed by a '('.
            r"(?P<path>\S+)"
            # Line number followed by a ','.
            r"\((?P<line>\d+),"
            # Column number followed by a ')', a ':' and a space.
            r"(?P<column>\d+)\): "
            # Severity followed by a space.
            r"(?P<severity>(error|warning)) "
            # Analyzer id followed by a ':' and a space.
            r"(?P<analyzer_id>\w+): "
            # Message followed by a space.
            r"(?P<message>[\S \t]+)\s* "
            # Project file location between a '[' and a ']'.
            r"\[(?P<project>[\S]+)\]"
        )

    def _parse_line(
        self,
        it: Iterator[str],
        line: str
    ) -> Tuple[List[Report], str]:
        """ Parse the given line. """
        match = self.message_line_re.match(line.lstrip())
        if match is None:
            return [], next(it)

        file_path = os.path.normpath(
            os.path.join(os.path.dirname(self.analyzer_result),
                         match.group('path')))

        report = Report(
            get_or_create_file(file_path, self._file_cache),
            int(match.group('line')),
            int(match.group('column')),
            match.group('message').strip(),
            match.group('analyzer_id'),
        )

        try:
            return [report], next(it)
        except StopIteration:
            return [report], ''
