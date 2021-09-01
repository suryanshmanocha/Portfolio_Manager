import seaborn as sns
from matplotlib import colors


def generate_colours(size, rgb=False):
    palette = sns.color_palette("mako", size)
    return palette if rgb else palette.as_hex()


# Wraps ticker information with styling
def coloured_data(data, **kwargs):
    size = len(data)

    def generate_greyed_colours():
        colours = generate_colours(size, rgb=True)
        greyed = []

        for colour in range(len(colours)):
            greyed_colour = []
            for rgb in range(3):
                darkened = colours[colour][rgb] / 1.2
                greyed_colour.append(darkened)
            greyed.append(tuple(greyed_colour))

        # convert rgb to hex
        hex = []
        for colour in greyed:
            hex.append(colors.to_hex(colour))

        return hex

    return {
        "data": data,
        "colours": generate_colours(size),
        "greyed_colours": generate_greyed_colours(),
        **kwargs,
    }

