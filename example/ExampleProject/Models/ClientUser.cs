using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ExampleProject.Models
{
    /// <summary>
    /// Represents the User that connected to the API.
    /// </summary>
    public class ClientUser : User
    {
        /// <summary>
        /// Gets the user's friends.
        /// </summary>
        /// <value>An array of Users that are friend with the current user.</value>
        /// <remarks>Only non-bot users can have friends.</remarks>
        public User[] Friends { get; private set; }
    }
}
