> **In production: close, supersede, never delete.**
> A regulated record keeps every state it passed through. A deviation moves to *Closed* with a root cause and a
> closing date; a protocol is *Superseded* with dates. The delete statements in the undo blocks would be unthinkable
> on a real deviation or batch record. Atomic transactions and unique constraints protect a single write; they do not
> protect two people running the same revision at once, which is why the Q22-style check stays in place as a backstop.
