# Simple file hosting for curl

## To upload file

```sh
curl -F file=@hello.txt __url__
```

## To download file

```sh
curl -O hello.txt __url__
```

## To delete file

```sh
curl -X DELETE __url__
```
