using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ExampleProject.Models
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
        public byte R{ get; private set; }
        /// <summary>
        /// Gets the greeb component of the color.
        /// </summary>
        /// <value>The greeb component of the color.</value>
        public byte G { get; private set; }
        /// <summary>
        /// Gets the blue component of the color.
        /// </summary>
        /// <value>The blue component of the color.</value>
        public byte B { get; private set; }

        /// <summary>
        /// Creates a color from its red, green and blue components respectively.
        /// </summary>
        /// <param name="r">Red component.</param>
        /// <param name="g">Green component.</param>
        /// <param name="b">Blue component.</param>
        public Color(int r, int g, int b)
        {
        }
    }
}
