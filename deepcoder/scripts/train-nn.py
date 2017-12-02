import argparse

from deepcoder.nn.model import get_model, load_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trainfile', type=str)
    parser.add_argument('--outfile', type=str)
    parser.add_argument('--epochs', type=int)
    parser.add_argument('--val_split', type=float)
    parser.add_argument('-E', type=int, 
        default=2, help='embedding dimension')
    parser.add_argument('--nb_inputs', type=int, default=3)
    args = parser.parse_args()

    with open(args.trainfile) as fh:
        X, y = load_data(fh, args.nb_inputs)

    model = get_model(args.nb_inputs, args.E)
    model.fit(X, y, epochs=args.epochs, validation_split=args.val_split)
    print('saving model to ', args.outfile)
    model.save(args.outfile)

if __name__ == '__main__':
    main()