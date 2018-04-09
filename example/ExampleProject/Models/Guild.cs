namespace Galarzaa.Api.Models
{
    /// <summary>
    /// Represents a guild.
    /// </summary>
    public class Guild
    {
        /// <summary>
        /// Gets the id.
        /// </summary>
        /// <value>The guild's id.</value>
        public int Id { get; private set; }

        /// <summary>
        /// Gets or sets the name.
        /// </summary>
        /// <value>The name of the guild.</value>
        public int Name { get; set; }

        /// <summary>
        /// Gets a channel in the guild with the given ID
        /// </summary>
		/// <param name="channelId">Id of the channel to look for.</param>
        /// <returns>The channel found</returns>
        public Channel GetChannel(int channelId){
            return new Channel();
        }
    }
}
