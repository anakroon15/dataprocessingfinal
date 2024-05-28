import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, Slider
from bokeh.layouts import column
from bokeh.io import curdoc
from bokeh.transform import factor_cmap
from bokeh.palettes import Category20

def load_data(filepath):
    """
    Load and clean data from a CSV file.
    Args: filepath (str): Path to CSV file.
    Returns: pandas.Dataframe: cleaned data
    """
    # load data
    data = pd.read_csv(filepath)
    # remove entries without essential data
    data.dropna(subset=['lifeExp', 'Fertility'], inplace=True)
    # forward and backward fill population data
    data['pop'] = data.groupby('Country')['pop'].ffill().bfill()
    # fill missing IDs with 'unknown'
    data['ID'] = data['ID'].fillna('Unknown')
    return data

def make_plot(source, initial_year):
    """
    Create a Bokeh plot with interactive tools.

    Args:
    source (ColumnDataSource): The source of data for glyphs.
    initial_year (int): Initial year to display on the plot.

    Returns:
    bokeh.plotting.figure: Configured plot.
    """
    # Prepare the color mapper for unique region data
    regions = list(set(source.data['Region']))
    color_mapper = factor_cmap('Region', palette=Category20[len(regions)] if len(regions) <= 20 else Category20[20], factors=regions)

    # setup plot with tools and styling
    p = figure(title=f"Life Expectancy vs Fertility in {initial_year}",
               x_axis_label='Fertility', y_axis_label='Life Expectancy',
               height=600, width=800, tools="pan,wheel_zoom,reset,save")

    # Scatter plot with culor based on region
    p.scatter(x='Fertility', y='lifeExp', size=10, source=source, color=color_mapper, line_color='black', fill_alpha=0.6)

    # Hover tool for additional data visibility
    hover = HoverTool(tooltips=[("Country", "@Country"), ("Population", "@pop"), ("Life Exp.", "@lifeExp"), ("Fertility", "@Fertility")])
    p.add_tools(hover)
    return p

def setup_slider(initial_year, source, plot, data):
    """
    Setup a slider for changing the year dynamically.

    Args:
    initial_year (int): The year to start the slider at.
    source (ColumnDataSource): Data source for the plot.
    plot (bokeh.plotting.figure): The plot to update.
    data (pandas.DataFrame): Full dataset for reference.

    Returns:
    bokeh.models.Slider: Configured slider for the plot.
    """
    # Slider for selecting year
    slider = Slider(start=1964, end=2013, value=initial_year, step=1, title="Year")

    def update_plot(attr, old, new):
        # update the data source based upon the selected year from the slider
        yr = slider.value
        new_data = data[data['Year'] == yr]
        source.data = new_data.to_dict(orient='list')
        plot.title.text = f"Life Expectancy vs Fertility in {yr}"

    slider.on_change('value', update_plot)
    return slider

def main():
    """
    Main function to setup and display the visualization
    """
    # Load and prepare data
    data = load_data('gapminder.csv')
    initial_year = 1964
    # prepare data source for the initial display
    source = ColumnDataSource(data=data[data['Year'] == initial_year])

    # setup plot and configure slider
    plot = make_plot(source, initial_year)
    slider = setup_slider(initial_year, source, plot, data)

    # Layout and add to document
    layout = column(plot, slider)
    curdoc().add_root(layout)

main()
