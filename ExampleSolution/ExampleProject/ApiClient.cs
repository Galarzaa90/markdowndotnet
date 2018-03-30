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
        /// <value>Authentication token for the account or Application.</value>
        public string token;

        /// <summary>
        /// Initializes a new instance of the <see cref="T:ExampleProject.ApiClient"/> class.
        /// </summary>
        public ApiClient()
        {
        }

        /// <summary>
        /// Logs in to the API
        /// </summary>
        /// <param name="token">The authentication token to use for login.</param>
		/// <returns><c>true</c> if login was successful, <c>false</c> otherwise.</returns>
        public bool Login(string token){
            this.token = token;
            return true;
        }

        /// <summary>
        /// Gets a channel with the specified id.
        /// </summary>
        /// <returns>Channel with the specified id</returns>
        /// <param name="channelId">The id of the channel.</param>
        public Channel GetChannel(int channelId){
            return new Channel();
        }

        /// <summary>
        /// Gets the guild by id.
        /// </summary>
        /// <param name="guildId">Guild id.</param>
        /// <returns>Guild with the specified id</returns>
        public Guild GetGuildById(int guildId){
            return new Guild();
        }
        /// <summary>
        /// Gets the user of the requester's account
        /// </summary>
        /// <returns>The current user</returns>
        public User GetMe(){
            return new User();
        }

        /// <summary>
        /// Gets the current user's guilds
        /// </summary>
        /// <returns>Guilds the token's user is in</returns>
        public Guild[] GetGuilds()
        {
            return new Guild[0];
        }
    }
}