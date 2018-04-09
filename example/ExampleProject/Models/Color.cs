namespace Galarzaa.Api.Models
{
    /// <summary>
    /// Represents a <see cref="Role"/> color.
    /// </summary>
    public class Color
    {
        /// <summary>
        /// Gets or sets the color's raw integer value.
        /// </summary>
        /// <value>The color's integer value.</value>
        public int Value { get; set; }
        /// <summary>
        /// Gets the red component of the color.
        /// </summary>
        /// <value>The red component of the color.</value>
        public byte R{ get;  }
        /// <summary>
        /// Gets the greeb component of the color.
        /// </summary>
        /// <value>The greeb component of the color.</value>
        public byte G { get;  }
        /// <summary>
        /// Gets the blue component of the color.
        /// </summary>
        /// <value>The blue component of the color.</value>
        public byte B { get; }

        /// <summary>
        /// Creates a color from its red, green and blue components respectively.
        /// </summary>
        /// <param name="r">Red component.</param>
        /// <param name="g">Green component.</param>
        /// <param name="b">Blue component.</param>
        public Color(int r, int g, int b)
        {
        }

        /// <summary>
        /// Creates a new color with the specified value.
        /// </summary>
        /// <param name="value">The raw integer value.</param>
        public Color(int value)
        {

        }

        /// <summary>
        /// Creates a instance of the class with the color red.
        /// </summary>
        /// <returns>Color with the value of <c>0xf40404</c></returns>
        public static Color Red()
        {
            return new Color(244, 4, 4);
        }

        /// <summary>
        /// Creates a instance of the class with the color teal.
        /// </summary>
        /// <returns>Color with the value of <c>0x1abc9c</c></returns>
        public static Color Teal()
        {
            return new Color(0x1abc9c);
        }
    }
}
