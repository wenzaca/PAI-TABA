# Dashboard Templates

This folder contains HTML templates for the dashboard visualizations.

## Structure

- `dashboard.html` - Main dashboard template with styling and layout

## Template Variables

The template uses placeholder variables that are replaced at runtime:

- `{{INSIGHTS_SECTION}}` - Analysis insights and statistical findings
- `{{PLOTLY_CHART}}` - Interactive Plotly visualization charts

## Usage

The `DashboardVisualizer` class automatically loads and populates this template when generating dashboards. You can customize the styling, layout, and structure by editing `dashboard.html`.

## Customization

To modify the dashboard appearance:

1. Edit the CSS in the `<style>` section
2. Adjust the HTML structure in the `<body>` section
3. Keep the `{{INSIGHTS_SECTION}}` and `{{PLOTLY_CHART}}` placeholders intact

The template is designed to be maintainable and separates presentation from data logic.
