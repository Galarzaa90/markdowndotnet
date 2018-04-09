namespace Galarzaa.Api.Models
{
    /// <summary>
    /// Represents the User that connected to the API.
    /// </summary>
    public class ClientUser : User
    {
        /// <summary>
        /// Gets the user's friends.
        /// </summary>
        /// <value>An array of Users that are friends with the current user.</value>
        /// <remarks>Only non-bot users can have friends.</remarks>
        public User[] Friends { get;  }

        /// <summary>
        /// Gets the list of users block by this user.
        /// </summary>
        /// <value>An array of Users that are blocked by the current user.</value>
        /// <remarks>Only non-bot users can block users.</remarks>
        public User[] Blocked { get;  }
    }
}
