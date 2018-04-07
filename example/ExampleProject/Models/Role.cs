using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ExampleProject.Models
{
    /// <summary>
    /// Represents a Role in a <see cref="Guild"/>.
    /// </summary>
    public class Role
    {
        /// <summary>
        /// Gets the unique id of the role
        /// </summary>
        /// <value>The unique id of the role.</value>
        public int Id { get; private set; }
        /// <summary>
        /// Gets the name of the role.
        /// </summary>
        /// <value>The name of the role.</value>
        public string Name { get; private set; }
        /// <summary>
        /// Gets the <see cref="Models.Guild"/> the role belongs to.
        /// </summary>
        /// <value>The guild the role belongs to.</value>
        public Guild Guild { get; private set; }
        /// <summary>
        /// Gets the color of the role.
        /// </summary>
        /// <value>The role's color.</value>
        public Color Color { get; private set; }
        /// <summary>
        /// Checks if the role will be displayed separately from other members.
        /// </summary>
        /// <value><c>true</c> if it will be displayed separately, <c>false</c> otherwise.</value>
        public bool Hoist { get; private set; }
        /// <summary>
        /// Gets the position of the role.
        /// </summary>
        /// <value>The position of the role.</value>
        /// <remarks>Bottom role has a position of 0.</remarks>
        public int Position { get; private set; }
        /// <summary>
        /// Checks if the role can be mentioned by users.
        /// </summary>
        /// <value><c>true</c> if it's mentionable, <c>false</c> otherwise.</value>
        public bool Mentionable { get; private set; }
        /// <summary>
        /// Checks if the role is the guild's default role.
        /// </summary>
        /// <value><c>true</c> if it is the default role, <c>false</c> otherwise.</value>
        public bool IsDefault { get; private set; }
    }
}
