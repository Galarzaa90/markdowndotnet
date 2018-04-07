using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ExampleProject.Models
{
    /// <summary>
    /// Represents a <see cref="User"/> in a <see cref="ExampleProject.Models.Guild"/>
    /// </summary>
    public class GuildUser : User
    {
        /// <summary>
        /// Gets the roles the user has in this guild.
        /// </summary>
        /// <value>An array of <see cref="Role"/>s</value>
        public Role[] Roles { get; }

        /// <summary>
        /// Gets the date when the user joined this guild.
        /// </summary>
        /// <value>The join date in UTC.</value>
        public DateTime JoinedAt { get; }

        /// <summary>
        /// Gets the guild where this user belongs to.
        /// </summary>
        /// <value>The guild where this user is.</value>
        public Guild Guild { get; }
        
        /// <summary>
        /// Gets the user's nickname.
        /// </summary>
        /// <value>The user's nickname if set, otherwise <c>null</c>.</value>
        public string Nick { get; }

        /// <summary>
        /// Gets the user's display name
        /// </summary>
        /// <remarks>The display name consist of the user's <see cref="Nick"/> (if set) or the user's <see cref="User.Name"/>.</remarks>
        /// <value>The user's display name.</value>
        public override string DisplayName { get; }
    }
}
