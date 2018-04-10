using Galarzaa.Api.Models;

namespace Galarzaa.Api.Delegates
{
    /// <summary>
    /// Delegate for the <see cref="Client.OnMessageReceived"/> event.
    /// </summary>
    /// <param name="message">The message received</param>
    public delegate void OnMessageHandler(Message message);
}
