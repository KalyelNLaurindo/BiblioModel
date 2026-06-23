import os
import csv
from datetime import date
from typing import List, Optional
from src.app.ports import IReportExporter

class ReportExporter(IReportExporter):
    """
    Concrete adapter for exporting data in CSV or HTML.
    Includes workspace bounds protection.
    """

    def export_report(
        self,
        report_type: str,
        format_type: str,
        headers: List[str],
        rows: List[List[str]],
        output_path: Optional[str] = None
    ) -> str:
        """
        Export a report to CSV or HTML format and write it to the output path.
        Returns the path where the report was saved.
        """
        if not output_path:
            output_path = os.path.join(
                "reports",
                f"export_{report_type}_{date.today().isoformat()}.{format_type}"
            )

        # Prevent Path Traversal
        workspace_dir = os.path.abspath(".")
        target_path = os.path.abspath(output_path)
        if not target_path.startswith(workspace_dir):
            raise PermissionError("Security Error: Output path must be within the project workspace.")

        # Create directory if it doesn't exist
        dir_name = os.path.dirname(target_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        if format_type.lower() == "csv":
            with open(target_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
        elif format_type.lower() == "html":
            rows_html = ""
            for row in rows:
                cols_html = "".join(f"<td style='padding: 8px; border: 1px solid #ddd;'>{cell}</td>" for cell in row)
                rows_html += f"<tr>{cols_html}</tr>"
            headers_html = "".join(f"<th style='padding: 8px; border: 1px solid #ddd; background-color: #f4f4f4; text-align: left;'>{h}</th>" for h in headers)
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Library Report - {report_type.capitalize()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}
        h1 {{ color: #2c3e50; }}
    </style>
</head>
<body>
    <h1>Library Report: {report_type.capitalize()}</h1>
    <p>Generated on: {date.today().isoformat()}</p>
    <table>
        <thead>
            <tr>{headers_html}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
</body>
</html>"""
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

        return output_path
