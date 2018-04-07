using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ExampleProject.Models
{
    /// <summary>
    /// Represents the possible user status
    /// </summary>
    public enum Status
    {
        /// <summary>
        /// User is online.
        /// </summary>
        ONLINE,
        /// <summary>
        ///  User is offline.
        /// </summary>
        OFFLINE,
        /// <summary>
        /// User is idle or set the idle status.
        /// </summary>
        IDLE,
        /// <summary>
        /// User is in do not disturb mode.
        /// </summary>
        DO_NOT_DISTURB,
        /// <summary>
        /// User is invisible.
        /// </summary>
        INVISIBLE
    }
}
