using Galarzaa.Api.Models;

namespace Galarzaa.Api
{
    /// <summary>
    /// Represents a connection to the client
    /// </summary>
    public class Client
    {
        /// <summary>
        /// Authentication token
        /// </summary>
        /// <value>Authentication token for the account or Application.</value>
        public string token;

        /// <summary>
        /// Gets a list of all the visible users.
        /// </summary>
        /// <value>Array containing all users the <see cref="ClientUser"/> can see.</value>
        public User[] Users { get; private set; }

        /// <summary>
        /// Event received every time a <see cref="Message"/> is received on any <see cref="Channel"/> the client sees.
        /// </summary>
        public event OnMessageHandler OnMessageReceived;

        /// <summary>
        /// Initializes a new instance of the <see cref="Client"/> class.
        /// </summary>
        public Client()
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
        /// Gets a <see cref="Guild"/> with the specified id.
        /// </summary>
        /// <param name="guildId">The unique id of the guild.</param>
        /// <returns>The guild found, or <c>null</c>.</returns>
        public Guild GetGuild(int guildId)
        {
            return new Guild();
        }

        /// <summary>
        /// Gets a <see cref="User"/> with the specified id.
        /// </summary>
        /// <param name="userId">The unique id of the user.</param>
        /// <returns>The user found, or <c>null</c>.</returns>
        public User GetUser(int userId)
        {
            return new User();
        }
    }
}