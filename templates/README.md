# Dashboard Templates

This folder contains HTML templates for the dashboard visualizations.

## Structure

- `dashboard.html` - Main dashboard template with styling and layout
- `insight_card.html` - Template for individual insight cards

## Template Variables

### dashboard.html
The main template uses placeholder variables that are replaced at runtime:

- `{{INSIGHTS_SECTION}}` - Analysis insights and statistical findings
- `{{PLOTLY_CHART}}` - Interactive Plotly visualization charts

### insight_card.html
The insight card template uses:

- `{{TITLE}}` - Card title (e.g., "Analysis 1: Emissions-Demographics Relationship")
- `{{CONTENT}}` - Card content (dynamically generated HTML with statistics)

## Usage

The `DashboardVisualizer` class automatically loads and populates these templates when generating dashboards. 

### Template Loading Flow

1. Load `dashboard.html` as the main structure
2. Load `insight_card.html` for each analysis section
3. Generate dynamic content (statistics, correlations, trends)
4. Inject Plotly charts
5. Write final HTML to output

## Customization

### Styling
Edit the CSS in `dashboard.html` `<style>` section to change:
- Colors and gradients
- Card layouts and spacing
- Typography and fonts
- Responsive breakpoints

### Layout
Modify the HTML structure in `dashboard.html` to:
- Rearrange sections
- Add new information cards
- Change grid layouts

### Insight Cards
Edit `insight_card.html` to:
- Change card structure
- Add icons or badges
- Modify content layout

**Important**: Keep placeholder variables (`{{VARIABLE}}`) intact for dynamic content injection.

## Design Philosophy

The template system separates:
- **Presentation** (HTML/CSS) - in template files
- **Data Logic** (Python) - in dashboard_visualizer.py
- **Dynamic Content** (Statistics) - generated at runtime

This makes the codebase more maintainable and allows designers to work independently from data scientists.
