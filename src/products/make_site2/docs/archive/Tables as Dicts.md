# Tables as Dicts

A **basic table spec** is an ordered list of basic sorts, with the table row extent (n) understood externally:

```text
[X, Y, Z]
```

A more general **table spec** allows columns to be grouped recursively. Structurally, it is an ordered nested dict whose terminal values are basic sorts:

```text
TableSpec ::= S+
S ::= <k> : (<t> | TableSpec)
```

Here, `<k>` is a key, `<t>` is a basic sort, and `S+` is a nonempty ordered list of keyed specifications.

Sibling keys in any one `D` must be unique. The same key may occur in different nested dicts, because a leaf column is identified by the full path of keys leading to it.

This is an abstract account. It does not assign rendering, display-heading, data-binding or implementation meaning to keys.

## Example

```text
[
  buyer: [
    name: String,
    address: String
  ],
  seller: [
    name: String,
    address: String
  ]
]
```

The terminal heading `name` appears twice, but the columns are unambiguous because their paths differ:

```text
buyer.name     : String
buyer.address  : String
seller.name    : String
seller.address : String
```

Erasing keys and nesting recovers the underlying basic table spec:

```text
[String, String, String, String]
```

Thus a table spec is an ordered recursive dict of keyed column sorts, where nested dict structure groups columns and paths uniquely address repeated leaf headings.
