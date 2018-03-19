using System;
namespace ExampleProject.Models
{
    /// <summary>
    /// Represents a User
    /// </summary>
    public class User
    {
        /// <summary>
        /// Gets the id.
        /// </summary>
        /// <value>The user's id.</value>
        public int Id { get; private set; }

        /// <summary>
        /// Gets or sets the name.
        /// </summary>
        /// <value>The name of the user.</value>
        public int Name { get; set; }

        /// <summary>
        /// Gets all guilds the user is in.
        /// </summary>
        /// <returns>The guild the user belongs to</returns>
        public Guild[] GetGuilds()
        {
            return new Guild[0];
        }
    }

}
