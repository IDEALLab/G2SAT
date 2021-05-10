from args import *
from model import *
from train import *
from data import *
from utils import *
from tensorboardX import SummaryWriter

### args
args = make_args()
print(args)
np.random.seed(123)
args.name = '{}_{}_{}_pre{}_drop{}_yield{}_{}'.format(args.model, args.layer_num, args.hidden_dim, args.feature_pre,
                                                      args.dropout, args.yield_prob, args.comment)

### set up gpu
if args.gpu:
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.cuda)
    print('Using GPU {}'.format(os.environ['CUDA_VISIBLE_DEVICES']))
else:
    print('Using CPU')
device = torch.device('cuda:' + str(args.cuda) if args.gpu else 'cpu')

### create graph templates to initailize generator
if not os.path.isdir('graphs/'):
    os.mkdir('graphs/')
template_name = 'graphs/template_small.dat'
train_name = 'graphs/train_small.dat'

print('args.recompute_template:', args.recompute_template)
args.recompute_template = True  # use this line to recompute for circuit stats. Not sure why had to do this...
if args.recompute_template or not os.path.isfile(template_name):
    # graphs_train, nodes_par1s_train, nodes_par2s_train = load_graphs_lcg(
    #     data_dir='dataset/train_set/', stats_dir='dataset/')
    graphs_train, nodes_par1s_train, nodes_par2s_train = load_graphs_lcg_LENS(
        data_dir='dataset_LENS/train_set/', stats_dir='dataset_LENS/')
    save_graph_list(
        graphs_train, train_name, has_par=True, nodes_par1_list=nodes_par1s_train, nodes_par2_list=nodes_par2s_train)
    print('Train graphs saved!', len(graphs_train))
    node_nums = [graph.number_of_nodes() for graph in graphs_train]
    edge_nums = [graph.number_of_edges() for graph in graphs_train]
    print('Num {}, Node {} {} {}, Edge {} {} {}'.format(
        len(graphs_train), min(node_nums), max(node_nums),
        sum(node_nums) / len(node_nums), min(edge_nums), max(edge_nums),
        sum(edge_nums) / len(edge_nums)))

    dataset_train = Dataset_sat(
        graphs_train, nodes_par1s_train, nodes_par2s_train, epoch_len=5000, yield_prob=args.yield_prob, speedup=False)

    graph_templates, nodes_par1s, nodes_par2s = dataset_train.get_template_fast()
    save_graph_list(
        graph_templates, template_name, has_par=True, nodes_par1_list=nodes_par1s, nodes_par2_list=nodes_par2s)
    print('Template saved!')
else:
    graph_templates, nodes_par1s, nodes_par2s = load_graph_list(template_name, has_par=True)
    print('Template loaded!')
    # print(len(nodes_par1s), len(nodes_par2s))  # 24, 24

print(graph_templates[0].number_of_nodes())

print('Template num', len(graph_templates))

# load stats
# with open('dataset/' + 'lcg_stats.csv') as csvfile:
with open('dataset_LENS/' + 'circuit_stats.csv') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    stats = []
    for stat in data:
        stats.append(stat)
generator_list = []
for i in range(len(graph_templates)):
    # find clause num
    for stat in stats:  #XD: loop through existing graphs, find the nearest one to the template
        # if int(stat[1]) == len(nodes_par1s[i]) // 2:  #XD: For SAT problems, n_var * 2  = #nodes_par1
        #     clause_num = int(int(stat[2]) * args.clause_ratio)
        #     break
        """XD: For LENS circuits, use this instead"""
        if int(stat[1]) == len(nodes_par1s[i]):
            clause_num = int(int(stat[2])* args.clause_ratio)
            break
        """XD"""
    # print('clause number =', clause_num)
    # assert clause_num is not None

    for j in range(args.gen_graph_num):  #XD: #generated_graphs per graph_template. Defalut is 1. 
        generator_list.append(
            graph_generator(
                graph_templates[i],
                len(nodes_par1s[i]),
                sample_size=args.sample_size,
                device=device,
                clause_num=clause_num))
print('length of generator_list:', len(generator_list))

input_dim = 3  # 3 node types
model = locals()[args.model](
    input_dim=input_dim,
    feature_dim=args.feature_dim,
    hidden_dim=args.hidden_dim,
    output_dim=args.output_dim,
    feature_pre=args.feature_pre,
    layer_num=args.layer_num,
    dropout=args.dropout).to(device)
model_fname = 'model/' + args.name + str(args.epoch_load)
model.load_state_dict(torch.load(model_fname, map_location=device))
model.to(device)
model.eval()
print('Model loaded!', model_fname)

test(args, generator_list, model, repeat=args.repeat)
