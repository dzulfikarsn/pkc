# invpend_description

Deskripsi robot inverted pendulum (cart-pole): rel (`slidebar`), `cart`, dan `pole`.

| Joint            | Tipe       | Sumbu | Keterangan                          |
|------------------|------------|-------|-------------------------------------|
| `slider_to_cart` | prismatic  | x     | diaktuasi dengan effort (N), ±2.5 m |
| `cart_to_pole`   | continuous | y     | pasif, 0 rad = pole tegak           |

Sudut pole positif berarti ujung pole condong ke arah +x.

## Struktur

```
urdf/
  invpend.urdf.xacro          # file utama (dipakai display.launch.py)
  invpend.description.xacro   # macro xacro:invpend_description
  invpend.materials.xacro     # warna RViz
config/urdf.rviz
launch/display.launch.py
```

## Menjalankan

```bash
ros2 launch invpend_description display.launch.py
```

## Lisensi

Geometri URDF diturunkan dari [linZHank/invpend_experiment](https://github.com/linZHank/invpend_experiment)
(MIT License, Copyright (c) 2018 linZHank). Nilai inersia sudah dikoreksi
(sebelumnya `iyy` pole bernilai 0, padahal pole berputar pada sumbu y).
