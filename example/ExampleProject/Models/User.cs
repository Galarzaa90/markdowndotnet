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
        /// Gets the user's display name
        /// </summary>
        /// <remarks>This property always returns the <see cref="Name"/> of the user. This property's behaviour changes in <see cref="GuildUser"/></remarks>
        /// <value>The user's display name.</value>
        public virtual string DisplayName { get; }

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
        /// Gets a string that allows you to mention the user
        /// </summary>
        /// <value>String that mentions the user in messages.</value>
        public string Mention { get; }

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
