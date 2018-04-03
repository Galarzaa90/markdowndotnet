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
        public string Name { get; private set; }

        /// <summary>
        /// Gets the user's discriminator.
        /// </summary>
        /// <value>A four character numeric discriminator.</value>
        public string Discriminator { get; private set; }

        /// <summary>
        /// Checks if the user is a bot user.
        /// </summary>
        /// <value><c>true</c> if the user is a bot, <c>false</c> otherwise.</value>
        public bool IsBot { get; private set; }

        /// <summary>
        /// Gets the user's creation date.
        /// </summary>
        /// <value>The creation date in UTC.</value>
        public DateTime CreationDate { get; private set; }

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
