# Simple file hosting for curl

## To upload file

```
curl -F file=@hello.txt __url__
```

## To download file

```
curl -O hello.txt __url__
```

## To delete file

```
curl -X DELETE __url__
```
