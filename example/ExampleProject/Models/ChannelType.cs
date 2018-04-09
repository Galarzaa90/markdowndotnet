namespace Galarzaa.Api.Models
{
    /// <summary>
    /// Represents the different channel types available.
    /// </summary>
    public enum ChannelTypes
    {
        /// <summary>
        /// Text channel in a guild.
        /// </summary>
        GUILD_TEXT,
        /// <summary>
        /// Private channel between two users.
        /// </summary>
        DM,
        /// <summary>
        /// Voice channel in a guild.
        /// </summary>
        GUILD_VOICE,
        /// <summary>
        /// Private group channel.
        /// </summary>
        GROUP_DM,
        /// <summary>
        /// Channel category in a guild.
        /// </summary>
        GUILD_CATEGORY

    }
}
