# TAGAPT: Towards Automatic Generation of Advanced Persistent Threat Samples with Provenance-level Granularity

## 1. AAG Generator

- Model training. The number of training rounds is 3. The models generated in each round are saved and stored in ./save_pretrain/exp_ASG_CTI_epoch3_1gpu/.

```sh
python -u -W ignore train_CTI.py --path ./data_preprocessed/CTI --train --num_workers 4 --batch_size 4 --lr 0.001 --epochs 3 --shuffle --deq_coeff 0.9 --save --name CTI_epoch3_1gpu --num_flow_layer 12 --nhid 128 --nout 128 --gcn_layer 3 --is_bn --divide_loss --st_type exp --seed 2019 --all_save_prefix ./
```

- AAG generation, the results are saved at ./CTIs/100asg

```sh
python -u -W ignore train_CTI.py --path ./data_preprocessed/CTI --gen --gen_out_path ./CTIs/100asg.txt --batch_size 32 --lr 0.001 --epochs 100 --shuffle --deq_coeff 0.9 --save --name l12_h128_o128_exp_sbatch --num_flow_layer 12 --nhid 128 --nout 128 --gcn_layer 3 --is_bn --divide_loss --st_type exp --init_checkpoint ./save_pretrain/exp_ASG_CTI_epoch3_1gpu/checkpoint2 --gen_num 100 --min_atoms 10 --save --seed 66666666 --temperature 0.7
```

- Process the generated AAG

```sh
python trans_gendata_CTI.py --directory_path ./CTIs --new_directory_path ./CTIs_trans/onerow --new_directory_path_multirow ./CTIs_trans/multirow --new_directory_path_multirow_divide ./CTIs_trans/multirow_divide --maxnode 100
```



## 2. AASG Divider

```sh
python Find_hub_process_test.py
```



## 3. IAG Builder

```sh
python graph_instance.py
```



## 4. Visualize IAG

```sh
python generate_subgraph_CTI.py --graph_path_txt ./result --graph_txt_path_2 ./result-visualization
```



## 5. Generated samples 

The generated samples are stored in "TAGAPT_samples"

# 