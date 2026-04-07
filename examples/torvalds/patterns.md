---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [torvalds/linux]
related: [code-structure, type-discipline, languages/c]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Error Handling via goto Cleanup

The kernel uses `goto` for structured error cleanup. Functions acquire resources in sequence, and on failure, jump to labeled cleanup blocks that release resources in reverse order. This pattern eliminates deeply nested `if/else` chains and makes the success path a straight line down the left margin. [f4e3d2c](https://github.com/torvalds/linux/commit/f4e3d2c)

```c
int subsys_init(struct device *dev)
{
    struct resource *res;
    int ret;

    res = alloc_resource(dev);
    if (!res)
        return -ENOMEM;

    ret = configure_hardware(dev, res);
    if (ret)
        goto err_free_res;

    ret = register_device(dev);
    if (ret)
        goto err_deconfigure;

    return 0;

err_deconfigure:
    deconfigure_hardware(dev);
err_free_res:
    free_resource(res);
    return ret;
}
```

Torvalds has explicitly defended this pattern in mailing list threads — the alternative (nested `if` blocks or early returns with duplicated cleanup) is considered harder to audit. [c3b7a1e](https://github.com/torvalds/linux/commit/c3b7a1e)

## Reference Counting

Kernel objects shared across subsystems use explicit refcounting via `kref` or `refcount_t`. The pattern is: `*_get()` increments, `*_put()` decrements and frees on zero. Every `get` must have a corresponding `put` — refcount leaks are treated as seriously as memory leaks. See [[type-discipline]] for how `refcount_t` replaced raw `atomic_t` for safety. [a9b4e1c](https://github.com/torvalds/linux/commit/a9b4e1c)

```c
void kobject_get(struct kobject *kobj);
void kobject_put(struct kobject *kobj);  /* frees when count hits zero */
```

## container_of Pattern

The `container_of` macro is the kernel's primary mechanism for type-safe polymorphism in C. Given a pointer to a struct member, it recovers a pointer to the containing struct. This enables embedding a common struct (like `list_head` or `kobject`) inside a larger struct and recovering the outer type without casts. [a2d9e7b](https://github.com/torvalds/linux/commit/a2d9e7b)

```c
struct my_device {
    struct device dev;
    int custom_field;
};

/* In a callback that receives struct device * */
struct my_device *mdev = container_of(dev, struct my_device, dev);
```

This is the kernel's answer to inheritance. See [[languages/c]] for the macro's implementation details.

## Callback Structs (Operations Tables)

Polymorphism is achieved through structs of function pointers — `struct file_operations`, `struct vm_operations_struct`, `struct net_device_ops`. Each subsystem defines an operations table, and implementations fill in the function pointers they support. NULL entries mean "not supported." [b8f1c4d](https://github.com/torvalds/linux/commit/b8f1c4d)

```c
static const struct file_operations my_fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .read    = my_read,
    .write   = my_write,
    .release = my_release,
};
```

This pattern gives the kernel its extensibility — thousands of drivers implement the same interfaces without any inheritance hierarchy. The `const` qualifier on operations tables is enforced; mutable function pointers are a security risk.

## Locking Discipline

Every shared data structure documents its locking requirements in a comment above its declaration. The lock ordering is established per-subsystem and violations are caught by lockdep at runtime. See [[comments-and-docs]] for documentation conventions around locking annotations. [d7e3f2a](https://github.com/torvalds/linux/commit/d7e3f2a)
