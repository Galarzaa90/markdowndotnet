using System;
using ExampleProject.Models;

namespace ExampleProject
{
    /// <summary>
    /// Represents a connection to the client
    /// </summary>
    public class ApiClient
    {
        /// <summary>
        /// Authentication token
        /// </summary>
        public string token;

        /// <summary>
        /// Initializes a new instance of the <see cref="T:ExampleProject.ApiClient"/> class.
        /// </summary>
        /// <param name="token">Authentication token.</param>
        public ApiClient(string token)
        {
            this.token = token;
        }

        /// <summary>
        /// Gets a channel with the specified id.
        /// </summary>
        /// <returns>Channel with the specified id</returns>
        /// <param name="channelId">The id of the channel.</param>
        public Channel GetChannelById(int channelId){
            return new Channel();
        }

        /// <summary>
        /// Gets the guild by id.
        /// </summary>
        /// <returns>Guild with the specified id</returns>
        /// <param name="guildId">Guild id.</param>
        public Guild GetGuildById(int guildId){
            return new Guild();
        }
    }
}