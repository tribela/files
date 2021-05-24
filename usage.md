# Simple file hosting for curl

## To upload file

```
curl -F file=@hello.txt __url__
http -f __url__ file@hello.txt
```

## To download file

```
curl -O hello.txt __url__
http --download __url__
```

## To delete file

```
curl -X DELETE __url__
http delete __url__
```
