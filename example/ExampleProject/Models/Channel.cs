using System;
namespace ExampleProject.Models
{
    /// <summary>
    /// Represents a channel
    /// </summary>
    public class Channel
    {
        /// <summary>
        /// Gets the channel's id
        /// </summary>
        /// <value>The channel's id.</value>
        public int Id { get; private set; }

        /// <summary>
        /// Gets the channel's type
        /// </summary>
        /// <value>The type of channel.</value>
        public ChannelTypes Type { get; }

        /// <summary>
        /// Initializes a new instance of the <see cref="T:ExampleProject.Models.Channel"/> class.
        /// </summary>
        public Channel()
        {
        }

        /// <summary>
        /// Gets the message with the specified id.
        /// </summary>
        /// <returns>The message.</returns>
        /// <param name="messageId">Message id.</param>
        public Message GetMessage(int messageId){
            return new Message();
        }


    }
}
