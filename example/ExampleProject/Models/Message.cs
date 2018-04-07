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
        /// Gets the message's channel.
        /// </summary>
        /// <value><see cref="ExampleProject.Models.Channel"/> where the message is.</value>
        public Channel Channel { get; private set; }

        /// <summary>
        /// Gets the guild that the message belongs to, if applicable
        /// </summary>
        /// <value><see cref="ExampleProject.Models.Guild"/> where the message is or <c>null</c>.</value>
        public Guild Guild { get; }


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
        /// Gets the time when the message was edited
        /// </summary>
        /// <value>The time when it was edited or <c>null</c> if not edited.</value>
        public DateTime EditedAt { get; }


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