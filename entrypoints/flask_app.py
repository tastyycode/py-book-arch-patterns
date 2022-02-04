from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import adapters.orm as orm
import domain.model as model
import config
import service_layer.services as services
import adapters.repository as repository

orm.starts_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)

@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    """Allocate"""
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty'],
    )

    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': e}), 400

    return jsonify({'batchref': batchref}), 201