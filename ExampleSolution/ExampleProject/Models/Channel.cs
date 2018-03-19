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
        /// Initializes a new instance of the <see cref="T:ExampleProject.Models.Channel"/> class.
        /// </summary>
        public Channel()
        {
        }


        public Message[] GetMessages(){
            return new Message[0];
        }

    }
}
