using System;

namespace ExampleProject.Models
{
    /// <summary>
    /// Represents a message.
    /// </summary>
    public class Message
    {

        /// <summary>
        /// Gets the unique id of the message
        /// </summary>
        /// <value>The unique id.</value>
        public int Id { get; private set; }

        /// <summary>
        /// Gets the author of the message.
        /// </summary>
        /// <value>The user that sent the message.</value>
        public User Author { get; private set; }

        /// <summary>
        /// Gets the message's guild.
        /// </summary>
        /// <value><see cref="ExampleProject.Models.Guild"/> where the message is, if applicable.</value>
        public Guild Guild { get; private set; }


        /// <summary>
        /// Gets the content of the message.
        /// </summary>
        public string Content { get; private set; }

        /// <summary>
        /// Gets the date the message was sent.
        /// </summary>
        /// <value>The date and time the message was sent in UTC.</value>
        public DateTime CreatedAt { get; private set; }


        /// <summary>
        /// Pins a message.
        /// </summary>
        /// <returns><c>true</c> if it was pinned successfully, <c>false</c> otherwise.</returns>
        public bool Pin()
        {
            return true;
        }

        /// <summary>
        /// Unpins a message.
        /// </summary>
        /// <returns><c>true</c> if it was unpinned successfully, <c>false</c> otherwise.</returns>
        public bool Unpin()
        {
            return true;
        }
    }
}